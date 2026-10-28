"""AI for the apps: the ia(pregunta, imagen=None) function they get.

The call is made here, on the server, with Yahoraque's key: the app only gets
the answer, never the key. To protect the free quota (the same one that
builds the apps), each app has DAILY_LIMIT calls a day, the lightest models
go first, and texts, images and answers have a maximum size. Repeating the
same question in a session reuses the answer instead of spending a call.
"""

import hashlib
import logging
from datetime import datetime, timezone

import streamlit as st

import llm
import prompts

DAILY_LIMIT = 30
MAX_TEXT_LENGTH = 10_000
MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_OUTPUT_TOKENS = 2048
IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp", "image/heic", "image/heif"}
# The app_check process uses this id: there, ia() must not run (no key, no quota).
CHECK_APP_ID = "check"
SYSTEM_PROMPT = prompts.load("ia_apps")["Instrucciones"]


class IAError(Exception):
    """A problem with ia() that the viewer should read (limit, unavailable…)."""


@st.cache_resource
def _calls_today():
    # Shared by all sessions: (app id, UTC date) -> calls. Resets if the server restarts.
    return {}


def _image(imagen):
    """{"data", "mime_type"} from what st.file_uploader returns, or None."""
    if imagen is None:
        return None
    if not (hasattr(imagen, "getvalue") and hasattr(imagen, "type")):
        raise IAError("La imagen tiene que venir de un botón para subir archivos.")
    if imagen.type not in IMAGE_TYPES:
        raise IAError("La imagen tiene que ser PNG, JPG o WEBP.")
    data = imagen.getvalue()
    if len(data) > MAX_IMAGE_BYTES:
        raise IAError("La imagen es demasiado grande: como mucho 5 MB.")
    return {"data": data, "mime_type": imagen.type}


def make_ia(app_id):
    """The ia() function for one app."""

    def ia(pregunta, imagen=None):
        if app_id == CHECK_APP_ID:
            raise IAError("ia() solo se puede usar al pulsar un botón, no al cargar la app.")
        if not isinstance(pregunta, str) or not pregunta.strip():
            raise IAError("No hay nada que preguntar a la IA.")
        if len(pregunta) > MAX_TEXT_LENGTH:
            raise IAError("El texto es demasiado largo para la IA: como mucho 10.000 caracteres.")
        image = _image(imagen)

        key = hashlib.sha256(pregunta.encode() + (image["data"] if image else b"")).hexdigest()
        answers = st.session_state.setdefault(f"app_{app_id}_ia_answers", {})
        if key in answers:
            return answers[key]

        calls = _calls_today()
        today = (app_id, datetime.now(timezone.utc).date().isoformat())
        if calls.get(today, 0) >= DAILY_LIMIT:
            raise IAError(
                f"Esta aplicación ya ha usado la IA {DAILY_LIMIT} veces hoy, que es el máximo. "
                "Vuelve a intentarlo mañana."
            )
        try:
            with st.spinner("La IA está pensando…"):
                answer = llm.generate(
                    SYSTEM_PROMPT,
                    [{"role": "user", "content": pregunta}],
                    image=image,
                    light=True,
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                )
        except llm.AIUnavailable as error:
            logging.warning("App %s: AI unavailable", app_id)
            raise IAError("La IA no está disponible ahora mismo. Inténtalo más tarde.") from error
        calls[today] = calls.get(today, 0) + 1
        logging.info("App %s used the AI (%s today)", app_id, calls[today])
        answers[key] = answer
        return answer

    return ia
