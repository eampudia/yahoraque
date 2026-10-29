import json

# Definición de la aplicación con la integración de IA solicitada
def ia_evaluacion(texto, nivel, criterios):
    prompt = f"""
    Eres un profesor experto de francés. Evalúa la siguiente redacción para un nivel {nivel}. 
    Criterios adicionales a observar: {criterios}.
    
    1. Primero, verifica si el texto está escrito mayoritariamente en francés. Si no, responde exactamente con la palabra "NO_FRANCES".
    2. Si es francés, evalúa el texto y devuelve un JSON con esta estructura exacta (sin formato adicional, solo el JSON):
    {{
        "nota": (número del 0 al 20),
        "desglose": {{"ortho": (0-5), "gram": (0-5), "voc": (0-5), "struct": (0-5)}},
        "errores": [ {{"type": "ortho|gram|voc|struct", "title": "...", "found": "...", "suggestion": "...", "explanation": "..."}} ],
        "repaso": ["punto 1", "punto 2"]
    }}
    Sé riguroso con la gramática, la ortografía (tildes francesas) y el nivel MCER indicado.
    
    Redacción: {texto}
    """
    try:
        resultado = ia(prompt)
        return resultado
    except:
        return "ERROR"

st.title("🇫🇷 Redacpro")
st.markdown("Evaluador pedagógico de redacciones en francés con escala sobre 20 puntos y detección estricta de idioma.")

# Estado de la sesión para persistir los datos de evaluación
if "resultado" not in st.session_state:
    st.session_state.resultado = None

# Configuración y entrada
col1, col2 = st.columns(2)
nivel = col1.selectbox("Nivel MCER:", ["A1", "A2", "B1", "B2", "C1", "C2"])
criterios = col2.text_input("Criterios a evaluar:", placeholder="Ej: Uso del futuro, Vocabulario...")

texto = st.text_area("Redacción en francés:")
archivo = st.file_uploader("O sube una foto con el texto:", type=["png", "jpg", "jpeg", "webp"])

if st.button("🔍 Evaluar Redacción"):
    texto_a_evaluar = texto
    if archivo:
        with st.spinner("Leyendo imagen..."):
            texto_a_evaluar = ia("Transcribe el texto en francés que aparece en esta imagen. Devuelve solo el texto transcrito.", imagen=archivo)
    
    if not texto_a_evaluar or len(texto_a_evaluar.strip()) < 5:
        st.warning("Por favor, escribe un texto o sube una imagen primero.")
    else:
        with st.spinner("Analizando redacción..."):
            res = ia_evaluacion(texto_a_evaluar, nivel, criterios)
            if res == "NO_FRANCES":
                st.session_state.resultado = {"error": "NO_FRANCES"}
            elif res == "ERROR":
                st.error("Hubo un error al procesar la IA. Inténtalo de nuevo.")
            else:
                try:
                    st.session_state.resultado = json.loads(res.replace("```json", "").replace("```", "").strip())
                except:
                    st.error("Formato de respuesta inesperado de la IA.")

# Mostrar resultados
if st.session_state.resultado:
    res = st.session_state.resultado
    if "error" in res:
        st.error("⚠️ La redacción no está escrita en francés. Calificación: 0 / 20")
    else:
        st.metric("Nota Final", f"{res['nota']} / 20")
        
        # Desglose en columnas
        d = res['desglose']
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Ortografía", f"{d['ortho']}/5")
        c2.metric("Gramática", f"{d['gram']}/5")
        c3.metric("Vocabulario", f"{d['voc']}/5")
        c4.metric("Estructura", f"{d['struct']}/5")
        
        st.subheader("🔎 Análisis de errores")
        for err in res['errores']:
            with st.expander(f"{err['type'].upper()}: {err['title']}"):
                st.write(f"**Encontrado:** {err['found']} ➔ **Sugerencia:** {err['suggestion']}")
                st.caption(err['explanation'])
        
        st.subheader("📌 Puntos de repaso")
        for p in res['repaso']:
            st.write(f"- {p}")

st.divider()
st.caption("Nota: Límite de 30 usos de IA al día. Los datos no se guardan al cerrar.")
