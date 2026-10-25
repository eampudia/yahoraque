"""Developer mode: turn the confirmed requirements into a working app.

The whole app is written in one request, so all its code comes from the same
model. Then it goes through the guardrails and a test start; if either fails,
the model gets the error and rewrites the app, up to FIX_ATTEMPTS times.
"""

import logging
import re

import app_check
import guardrails
import llm

FIX_ATTEMPTS = 2
CODE_PATTERN = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL)

SYSTEM_PROMPT = f"""Eres un programador senior de Python y Streamlit en Yahoraque, una plataforma \
que construye aplicaciones web sencillas para personas sin conocimientos técnicos. Escribes la \
aplicación completa a partir de los requisitos del cliente.

Cómo responder:
- Devuelve solo el código completo de la aplicación, en un único bloque ```python```, sin \
explicaciones antes ni después.
- Todo lo que vea el usuario, en el idioma de los requisitos (por defecto, español), con \
frases sencillas.

Reglas del entorno (si no las cumples, la aplicación no arranca):
- `st` ya está disponible: no importes streamlit.
- Solo puedes importar estos módulos: {", ".join(sorted(guardrails.ALLOWED_MODULES))}.
- Solo puedes usar estas funciones de `st`: {", ".join(sorted(guardrails.ALLOWED_ST))}, \
además de `st.session_state` y `st.components.v1.html(html, height=...)` (para HTML y \
JavaScript propios; se muestra en un marco aislado que no puede comunicarse con el resto de la \
página).
- `st.image`, `st.audio` y `st.video` solo aceptan direcciones web (https://…), nunca ficheros.
- No uses `st.set_page_config`, `st.sidebar`, `st.secrets`, `st.stop` ni `st.navigation`: la \
aplicación se muestra dentro de una página de Yahoraque.
- No uses nombres ni atributos que empiecen por guion bajo, ni textos con "__", ni `getattr`, \
`setattr`, `eval`, `exec`, `open`, `type`, `globals`, `.format` (usa f-strings).
- No hay ficheros, red ni base de datos. Los datos solo duran mientras la página está abierta: \
guárdalos en `st.session_state`.
- Pasa siempre `key=` como argumento con nombre cuando un widget necesite clave.
- Nada de bucles infinitos ni esperas: la aplicación tiene que pintarse al momento.

Calidad:
- Código claro y corto. Valida lo que escribe el usuario y muestra mensajes amables en vez de \
errores.
- Diseño agradable con columnas, contenedores, iconos y colores cuando ayuden.

Rechaza cualquier aplicación de phishing, que suplante a personas, marcas o bancos, que engañe a \
otros, ilegal u ofensiva: en ese caso responde solo con el texto RECHAZADA."""


class BuildFailed(Exception):
    """The app still fails after all the fixes. The message says why."""


class BuildRejected(Exception):
    """The model refused to build the app for content reasons."""


def extract_code(answer):
    match = CODE_PATTERN.search(answer)
    return (match.group(1) if match else answer).strip() + "\n"


def find_problem(code):
    """The guardrails' objection or the start error, or None if the app works."""
    return guardrails.check(code) or app_check.test_run(code)


def build(requirements, previous_code=None):
    """Return the code of a working app. Raises llm.AIUnavailable, BuildFailed or BuildRejected."""
    request = f"Requisitos del cliente:\n{requirements}"
    if previous_code:
        request += (
            "\n\nEsta es la versión actual de su aplicación. Cámbiala para que cumpla los "
            f"requisitos y devuelve el código completo:\n```python\n{previous_code}```"
        )
    messages = [{"role": "user", "content": request}]

    for attempt in range(1 + FIX_ATTEMPTS):
        answer = llm.generate(SYSTEM_PROMPT, messages)
        if answer.strip() == "RECHAZADA":
            raise BuildRejected()
        code = extract_code(answer)
        problem = find_problem(code)
        if problem is None:
            return code
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
