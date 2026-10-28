"""Developer mode: turn the confirmed requirements into a working app.

The whole app is written in one request, so all its code comes from the same
model. Then it goes through the guardrails and a test start; if either fails,
the model gets the error and rewrites the app, up to FIX_ATTEMPTS times.
In the same answer the model invents the app's name: one made-up word.
"""

import logging
import re

import app_ai
import app_check
import app_theme
import guardrails
import llm
import prompts

FIX_ATTEMPTS = 2
# Up to the LAST fence: AI apps often have ``` in their own code (to clean the
# answers of ia()), and stopping at the first one cut the app in half.
CODE_PATTERN = re.compile(r"```(?:python)?[ \t]*\n(.*)```", re.DOTALL)
# `st` is already given: weaker models often import it anyway.
STREAMLIT_IMPORT = re.compile(
    r"^[ \t]*(?:import streamlit\S*(?:[ \t]+as[ \t]+\w+)?|from streamlit\S*[ \t]+import[^\n]*)[ \t]*\n",
    re.MULTILINE,
)
NAME_PATTERN = re.compile(r"^\s*NOMBRE:\s*(\S+)", re.MULTILINE)
NAME_MAX_LENGTH = 20
DEFAULT_NAME = "Miapp"
LIBRARY_LIST = "\n".join(f"  - {use}: {url}" for use, url in app_theme.LIBRARIES.items())

# The text is in prompts/desarrollador.md; the lists come from the guardrails and the kit,
# so the instructions always match what is really allowed.
SYSTEM_PROMPT = prompts.fill(
    prompts.load("desarrollador")["Instrucciones"],
    LONGITUD_NOMBRE=NAME_MAX_LENGTH,
    MODULOS=", ".join(sorted(guardrails.ALLOWED_MODULES)),
    FUNCIONES_ST=", ".join(sorted(guardrails.ALLOWED_ST)),
    LIBRERIAS=LIBRARY_LIST,
    LIMITE_IA=app_ai.DAILY_LIMIT,
)


class BuildFailed(Exception):
    """The app still fails after all the fixes. The message says why."""


class BuildRejected(Exception):
    """The model refused to build the app for content reasons."""


def extract_code(answer):
    match = CODE_PATTERN.search(answer)
    # Without a code block, the whole answer is the code, minus the name line.
    code = match.group(1) if match else NAME_PATTERN.sub("", answer, count=1)
    return STREAMLIT_IMPORT.sub("", code.strip() + "\n")


def extract_name(answer):
    """The made-up name, cleaned to letters only."""
    match = NAME_PATTERN.search(answer)
    letters = "".join(char for char in match.group(1) if char.isalpha()) if match else ""
    return letters[:NAME_MAX_LENGTH].capitalize() or DEFAULT_NAME


def unknown_libraries_problem(code):
    unknown = app_theme.unknown_libraries(code)
    if unknown:
        return "Librerías no permitidas (usa solo las de la lista): " + ", ".join(unknown)
    return None


def find_problem(code):
    """The guardrails' objection or the start error, or None if the app works."""
    return (
        guardrails.check(code)
        or unknown_libraries_problem(code)
        or app_check.test_run(code)
    )


def build(requirements, previous_code=None, name=None):
    """Return (code, name) of a working app. Raises llm.AIUnavailable, BuildFailed or BuildRejected.

    An app that already has a name keeps it.
    """
    request = f"Requisitos del cliente:\n{requirements}"
    if previous_code:
        request += (
            "\n\nEsta es la versión actual de su aplicación. Cámbiala para que cumpla los "
            f"requisitos y devuelve el código completo:\n```python\n{previous_code}```"
        )
    if name:
        request += f"\n\nLa aplicación ya se llama {name}: usa NOMBRE: {name}."
    messages = [{"role": "user", "content": request}]

    for attempt in range(1 + FIX_ATTEMPTS):
        answer = llm.generate(SYSTEM_PROMPT, messages)
        if answer.strip() == "RECHAZADA":
            raise BuildRejected()
        code = extract_code(answer)
        problem = find_problem(code)
        if problem is None:
            return code, name or extract_name(answer)
        logging.warning("Build attempt %s failed: %s", attempt + 1, problem)
        messages += [
            {"role": "assistant", "content": answer},
            {
                "role": "user",
                "content": f"La aplicación no funciona:\n{problem}\n\n"
                "Corrígela y devuelve el código completo.",
            },
        ]
    raise BuildFailed(problem)
