"""Funny phrases shown while waiting for the AI.

The AI call runs in a background thread while the page shows a spinner with
a phrase that changes every few seconds. Phrases come from a shuffled deck
kept in the session, so none repeats until all of them have been shown.
"""

import random
import threading

import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

ROTATE_SECONDS = 3
PHRASES = [
    "Afilando los lápices…",
    "Despertando a las neuronas del turno de noche…",
    "Consultando con mi gato, que sabe mucho de esto…",
    "Preparándome un café bien cargado para pensar mejor…",
    "Ordenando tus ideas por colores…",
    "Buscando la pregunta perfecta debajo del sofá…",
    "Haciendo garabatos en una servilleta…",
    "Calentando motores… brum, brum…",
    "Pidiéndole consejo a mi abuela…",
    "Contando hasta diez para no precipitarme…",
    "Dándole vueltas, como a un buen cocido…",
    "Poniéndome las gafas de pensar…",
    "Sacudiendo la bola de cristal…",
    "Desenredando la madeja de ideas…",
    "Uniendo los puntos para ver el dibujo…",
    "Mirando por la ventana con cara de genio…",
    "Explicándoselo todo a mi pato de goma…",
    "Rascándome la cabeza con elegancia…",
    "Apuntándolo todo en mi libreta mágica…",
    "Probando ideas en la pizarra…",
    "Encendiendo la bombilla… un momento, que parpadea…",
    "Mezclando los ingredientes de tu receta…",
    "Consultándolo con la almohada, pero en versión rápida…",
    "Montando el puzle pieza a pieza…",
    "Hinchando el globo de las ideas…",
    "Pasando la aspiradora a las ideas malas…",
    "Echando cuentas con los dedos…",
    "Regando el huerto de las ideas…",
    "Sacándole brillo a tu idea…",
    "Buscando las llaves de la inspiración…",
    "Ensayando mi mejor respuesta delante del espejo…",
    "Dibujando planos con mucho cariño…",
    "Atando cabos sueltos…",
    "Pensando tan fuerte que casi se oye…",
    "Inflando las ruedas de la creatividad…",
    "Leyendo el manual de instrucciones del universo…",
    "Haciendo estiramientos mentales…",
    "Persiguiendo una idea que se me ha escapado…",
    "Afinando la guitarra antes de tocar tu canción…",
    "Haciendo malabares con tus ideas…",
]

# Our own spinner: replacing its text does not make it blink like st.spinner.
SPINNER_HTML = """\
<style>@keyframes yq-spin {{ to {{ transform: rotate(360deg); }} }}</style>
<div style="display: flex; align-items: center; gap: 0.6rem; opacity: 0.8;">
  <span style="width: 1rem; height: 1rem; border: 2px solid currentColor;
    border-right-color: transparent; border-radius: 50%;
    animation: yq-spin 0.8s linear infinite;"></span>
  <span>{phrase}</span>
</div>"""


def next_phrase():
    deck = st.session_state.get("phrase_deck")
    if not deck:
        deck = random.sample(PHRASES, len(PHRASES))
        st.session_state.phrase_deck = deck
    return deck.pop()


def run(function, *args):
    """Return function(*args), showing funny phrases until it finishes.

    Exceptions raised by the function reach the caller unchanged.
    """
    outcome = {}

    def target():
        try:
            outcome["value"] = function(*args)
        except Exception as error:
            outcome["error"] = error

    thread = threading.Thread(target=target, daemon=True)
    # Lets the function use Streamlit's caches and secrets from the thread.
    add_script_run_ctx(thread, get_script_run_ctx())
    placeholder = st.empty()
    thread.start()
    try:
        while thread.is_alive():
            placeholder.markdown(
                SPINNER_HTML.format(phrase=next_phrase()), unsafe_allow_html=True
            )
            thread.join(ROTATE_SECONDS)
    finally:
        placeholder.empty()

    if "error" in outcome:
        raise outcome["error"]
    return outcome["value"]
