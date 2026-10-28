"""Analyst mode: talk with the user until the requirements are clear.

When the model has enough information it writes the requirements between
the REQUIREMENTS_START and REQUIREMENTS_END markers; the page shows them
and asks the user to confirm.
"""

import re

import app_ai
import llm
import prompts

REQUIREMENTS_START = "<<REQUISITOS>>"
REQUIREMENTS_END = "<<FIN>>"
REQUIREMENTS_PATTERN = re.compile(
    re.escape(REQUIREMENTS_START) + r"(.*?)" + re.escape(REQUIREMENTS_END), re.DOTALL
)

GREETING = (
    "¡Hola! Soy tu analista. Cuéntame con tus palabras qué te gustaría que hiciera "
    "tu aplicación y para qué la quieres. No hace falta que sepas nada técnico."
)

# The texts are in prompts/analista.md.
_PROMPTS = prompts.load("analista")
SYSTEM_PROMPT = prompts.fill(
    _PROMPTS["Instrucciones"],
    MARCA_INICIO=REQUIREMENTS_START,
    MARCA_FIN=REQUIREMENTS_END,
    LIMITE_IA=app_ai.DAILY_LIMIT,
)
CURRENT_APP_PROMPT = "\n\n" + _PROMPTS["Si el cliente ya tiene una aplicación"]


def greeting(name=None):
    if name:
        return (
            f"¡Hola! Tu aplicación {name} ya está funcionando. "
            "Cuéntame qué te gustaría cambiar o añadir."
        )
    return GREETING


def reply(messages, current_app=None):
    """Return (text to show, requirements or None) for the next analyst turn.

    current_app: {"name", "requirements"} of the user's app, if there is one, so
    the analyst works on changes instead of starting from scratch.
    """
    system_prompt = SYSTEM_PROMPT
    if current_app:
        system_prompt += prompts.fill(
            CURRENT_APP_PROMPT, NOMBRE=current_app["name"], REQUISITOS=current_app["requirements"]
        )
    answer = llm.generate(system_prompt, messages)
    match = REQUIREMENTS_PATTERN.search(answer)
    if not match:
        return answer.strip(), None
    text = REQUIREMENTS_PATTERN.sub("", answer).strip()
    return text, match.group(1).strip()
