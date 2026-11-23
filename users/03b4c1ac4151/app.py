import json

st.title("🔥 Generador de Rimas Cochinotas")
st.markdown("Escribe una palabra y nuestro poeta gamberro creará una rima subida de tono para ti.")

if "rima" not in st.session_state:
    st.session_state.rima = ""

with st.form("rimas_form"):
    palabra = st.text_input("Introduce una palabra:", placeholder="Ej: melocotón, calcetín, tomate...")
    submit = st.form_submit_button("¡Generar rima picante!")

if submit:
    if not palabra:
        st.warning("¡Escribe algo primero, pedazo de artista!")
    else:
        with st.spinner("Pensando algo picante..."):
            prompt = (
                f"Escribe una rima muy gamberra, picante y atrevida de exactamente dos frases. "
                f"Cada frase debe tener al menos 4 palabras. "
                f"La rima debe estar relacionada con la palabra: '{palabra}'. "
                f"Usa un tono humorístico y sugerente. Devuelve solo el texto de la rima."
            )
            respuesta = ia(prompt)
            st.session_state.rima = respuesta

if st.session_state.rima:
    st.markdown("---")
    st.markdown(f"### 😈 La rima de hoy:")
    st.success(st.session_state.rima)
    st.markdown("---")

HTML = """
<div style="text-align: center; margin-top: 20px;">
    <p style="color: var(--yq-navy); font-size: 0.9em;">
        ¿Listo para otra? ¡Dale arriba a generar!
    </p>
</div>
<script>
    console.log("Rimatron activo y listo para la picardía.");
</script>
"""

st.components.v1.html(HTML, height=200)

st.caption("Nota: Esta aplicación tiene un límite de 30 consultas diarias compartidas. ¡Úsalas con sabiduría!")
