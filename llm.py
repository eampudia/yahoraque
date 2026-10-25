"""Gemini on the free tier: always use the most powerful model that works.

Models are listed from the API and ranked by name: newest version first,
then pro > flash > flash-lite, stable before preview. Each request tries
them in order. A failing model is skipped silently; one that ran out of
quota rests for a while so the next requests do not waste time on it.
"""

import logging
import re
import time

import streamlit as st
from google import genai
from google.genai import errors, types

import storage

MODEL_PATTERN = re.compile(r"^gemini-(\d+(?:\.\d+)*)-(pro|flash|flash-lite)(-preview)?$")
TIER_RANK = {"pro": 0, "flash": 1, "flash-lite": 2}
MINUTE = 60
DAY = 24 * 60 * 60
OVERLOADED_REST = 5 * MINUTE
# A model that does not answer in time is treated as failed.
REQUEST_TIMEOUT_MS = 60_000


class AIUnavailable(Exception):
    """Every model failed: the user sees the "astros" message."""


@st.cache_resource
def _client():
    api_key = storage.get_secret("GOOGLE_API_KEY")
    if not api_key:
        raise AIUnavailable("Falta el secreto GOOGLE_API_KEY.")
    # No retries inside the SDK: on failure we move on to the next model.
    http_options = types.HttpOptions(
        timeout=REQUEST_TIMEOUT_MS, retry_options=types.HttpRetryOptions(attempts=1)
    )
    return genai.Client(api_key=api_key, http_options=http_options)


@st.cache_resource
def _resting_until():
    # Shared by all sessions: model name -> time when it can be tried again.
    return {}


def rank_models(names):
    """Keep the text models and sort them from most to least powerful."""
    ranked = []
    for name in names:
        name = name.removeprefix("models/")
        match = MODEL_PATTERN.match(name)
        if match:
            version, tier, preview = match.groups()
            # Pad so "3" compares as 3.0.0 and sorts after "3.8".
            parts = [int(part) for part in version.split(".")] + [0, 0]
            newest_first = tuple(-part for part in parts[:3])
            ranked.append(((newest_first, TIER_RANK[tier], bool(preview)), name))
    return [name for _, name in sorted(ranked)]


@st.cache_data(ttl=3600, show_spinner=False)
def available_models():
    names = [
        model.name
        for model in _client().models.list()
        if "generateContent" in (model.supported_actions or [])
    ]
    return rank_models(names)


def _rest_seconds(error):
    if error.code == 429:
        message = str(error)
        if "limit: 0" in message or "PerDay" in message:
            return DAY
        return MINUTE
    if error.code in (403, 404):
        # Not usable with this key.
        return DAY
    if error.code >= 500:
        # Overloaded or too slow: give it a break so users do not wait on it again.
        return OVERLOADED_REST
    # 400 may be our own mistake: do not bench the model.
    return 0


def generate(system_prompt, messages):
    """Answer a conversation.

    messages: list of {"role": "user" | "assistant", "content": str}.
    """
    contents = [
        types.Content(
            role="model" if message["role"] == "assistant" else "user",
            parts=[types.Part.from_text(text=message["content"])],
        )
        for message in messages
    ]
    config = types.GenerateContentConfig(system_instruction=system_prompt)

    try:
        models = available_models()
    except Exception as error:
        logging.exception("Could not list models")
        raise AIUnavailable("No se han podido listar los modelos.") from error

    resting = _resting_until()
    for model in models:
        if resting.get(model, 0) > time.time():
            continue
        try:
            response = _client().models.generate_content(
                model=model, contents=contents, config=config
            )
        except errors.APIError as error:
            rest = _rest_seconds(error)
            if rest:
                resting[model] = time.time() + rest
            logging.warning("Model %s failed (%s), trying the next one", model, error.code)
            continue
        except Exception:
            # Usually a timeout or a network error.
            resting[model] = time.time() + OVERLOADED_REST
            logging.exception("Model %s failed, trying the next one", model)
            continue

        if response.text:
            logging.info("Model %s answered", model)
            return response.text
        logging.warning("Model %s returned no text, trying the next one", model)

    raise AIUnavailable("Todos los modelos han fallado.")
