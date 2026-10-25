"""Developer mode: turn the confirmed requirements into a working app.

The whole app is written in one request, so all its code comes from the same
model. Then it goes through the guardrails and a test start; if either fails,
the model gets the error and rewrites the app, up to FIX_ATTEMPTS times.
In the same answer the model invents the app's name: one made-up word.
"""

import logging
import re

import app_check
import app_theme
import guardrails
import llm

FIX_ATTEMPTS = 2
CODE_PATTERN = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL)
# `st` is already given: weaker models often import it anyway.
STREAMLIT_IMPORT = re.compile(
    r"^[ \t]*(?:import streamlit\S*(?:[ \t]+as[ \t]+\w+)?|from streamlit\S*[ \t]+import[^\n]*)[ \t]*\n",
    re.MULTILINE,
)
NAME_PATTERN = re.compile(r"^\s*NOMBRE:\s*(\S+)", re.MULTILINE)
NAME_MAX_LENGTH = 20
DEFAULT_NAME = "Miapp"
LIBRARY_LIST = "\n".join(f"  - {use}: {url}" for use, url in app_theme.LIBRARIES.items())

SYSTEM_PROMPT = f"""Eres un programador senior de JavaScript, HTML, CSS y Python en Yahoraque, \
una plataforma que construye aplicaciones web sencillas para personas sin conocimientos técnicos. \
Escribes la aplicación completa a partir de los requisitos del cliente.

Cómo se construye (siempre que sea posible):
- La aplicación es un fichero Python cuyo único trabajo es mostrar una página hecha con HTML, CSS y \
JavaScript: guarda la página completa en un texto triple (no uses f-string, por las llaves de \
JavaScript y CSS) y muéstrala con una sola llamada `st.components.v1.html(HTML, height=...)`.
- Toda la lógica y la interacción van en JavaScript, dentro de esa página: botones, formularios, \
cálculos, juegos, animaciones, gráficos. Así responde al momento, sin recargar.
- Elige `height` en píxeles para que se vea toda la aplicación sin cortes, incluidos los \
resultados que aparecen al usarla (por ejemplo, 600 a 1000): mejor que sobre a que falte. El \
marco no crece solo: si el contenido puede ser largo, deja que la página tenga scroll.
- Si necesitas pasar datos de Python a la página, ponlos con `json.dumps` en lugar de una marca \
del texto usando `.replace`.
- Usa widgets de Streamlit (`st.button`, `st.text_input`…) solo si algo no se puede hacer en el \
navegador.

Reglas de la página HTML/JavaScript:
- Se muestra en un marco aislado: no puede comunicarse con el resto de la página de Yahoraque.
- No uses `localStorage`, `sessionStorage`, `indexedDB` ni cookies: dentro del marco dan error. \
Los datos viven en variables de JavaScript mientras la página está abierta.
- Yahoraque ya carga en la página Pico CSS 2 y su propio estilo (colores del logo, letras \
redondeadas): no los cargues tú. Usa HTML semántico (`main.container`, `article` como tarjeta, \
`button`, `form`, `label` + `input`, `fieldset`, `table`, `progress`, `details`…), que Pico ya \
pinta bonito, y escribe solo el CSS que falte.
- Colores de Yahoraque como variables CSS: `--yq-blue`, `--yq-green`, `--yq-yellow`, \
`--yq-purple`, `--yq-navy`. Úsalos para gráficas, etiquetas y detalles. No los redefinas ni \
cambies el color principal de Pico (el morado de Yahoraque): así todas las apps se ven de la casa.
- Solo puedes cargar estas librerías, con esta dirección exacta, y solo si hacen falta:
{LIBRARY_LIST}
- No cargues otras librerías ni llames a otras webs o APIs.
- Diseño adaptable al ancho del marco y que se lea bien en móvil.

Cómo responder:
- Primera línea: `NOMBRE: <palabra>`, con un nombre para la aplicación: una sola palabra \
inventada, fácil de pronunciar y de recordar, inspirada en los requisitos (por ejemplo, para un \
contador de vasos de agua, "Aguatín"). Solo letras, como mucho {NAME_MAX_LENGTH}, sin espacios \
ni números.
- Después, el código completo de la aplicación en un único bloque ```python```, sin \
explicaciones antes ni después.
- Todo lo que vea el usuario, en el idioma de los requisitos (por defecto, español), con \
frases sencillas. Números, fechas y dinero en el formato de ese idioma (en español: 1.234,56 € \
y 25/10/2026), salvo que los requisitos digan otra cosa.

Reglas del código Python (si no las cumples, la aplicación no arranca):
- `st` ya está disponible: no importes streamlit.
- Solo puedes importar estos módulos: {", ".join(sorted(guardrails.ALLOWED_MODULES))}.
- Solo puedes usar estas funciones de `st`: {", ".join(sorted(guardrails.ALLOWED_ST))}, \
además de `st.session_state` y `st.components.v1.html`.
- `st.image`, `st.audio` y `st.video` solo aceptan direcciones web (https://…), nunca ficheros.
- No uses `st.set_page_config`, `st.sidebar`, `st.secrets`, `st.stop` ni `st.navigation`: la \
aplicación se muestra dentro de una página de Yahoraque.
- No uses nombres ni atributos de Python que empiecen por guion bajo, ni `getattr`, `setattr`, \
`eval`, `exec`, `open`, `type`, `globals`, `.format` (usa f-strings o `.replace`).
- En Python no hay ficheros, red ni base de datos. Si usas widgets de Streamlit, sus datos van en \
`st.session_state` y pasa siempre `key=` como argumento con nombre.
- Nada de bucles infinitos ni esperas en Python: la aplicación tiene que pintarse al momento.

Calidad:
- Código claro. Valida lo que escribe el usuario y muestra mensajes amables en vez de errores.
- Revisa que el JavaScript no tenga errores: solo se comprueba automáticamente que el Python \
arranca, no el JavaScript.
- Diseño agradable, con colores, iconos (emojis) y espaciado cuidado.

Rechaza cualquier aplicación de phishing, que suplante a personas, marcas o bancos, que engañe a \
otros, ilegal u ofensiva: en ese caso responde solo con el texto RECHAZADA."""


class BuildFailed(Exception):
    """The app still fails after all the fixes. The message says why."""


class BuildRejected(Exception):
    """The model refused to build the app for content reasons."""


def extract_code(answer):
    match = CODE_PATTERN.search(answer)
    code = (match.group(1) if match else answer).strip() + "\n"
    return STREAMLIT_IMPORT.sub("", code)


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
