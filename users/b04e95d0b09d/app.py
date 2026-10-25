import random

if "flores" not in st.session_state:
    st.session_state.flores = []

if "fondo_actual" not in st.session_state:
    st.session_state.fondo_actual = "Atardecer Suave"

frases = [
    "Cada pequeño paso cuenta en tu camino hacia el éxito.",
    "Eres más fuerte de lo que imaginas y capaz de lograr lo que te propones.",
    "La actitud positiva abre puertas que las murallas cierran.",
    "Hoy es un día maravilloso para comenzar algo nuevo.",
    "Tus sueños merecen toda tu energía y dedicación.",
    "Cultiva pensamientos alegres y tu mente florecerá.",
    "La paciencia y la constancia transforman los retos en triunfos.",
    "Ilumina el mundo con tu sonrisa única y auténtica.",
    "No hay límite para lo que puedes alcanzar cuando crees en ti.",
    "Cada flor nace a su propio ritmo; date el tiempo de crecer."
]

fondos = {
    "Atardecer Suave": "linear-gradient(135deg, #fbc531, #e84118)",
    "Pradera Fresca": "linear-gradient(135deg, #4cd137, #009432)",
    "Cielo Pastel": "linear-gradient(135deg, #00d2d3, #54a0ff)",
    "Atardecer Romántico": "linear-gradient(135deg, #ff9ff3, #f368e0)"
}

colores_flor = ["#ff4757", "#2ed573", "#1e90ff", "#ffa502", "#9b59b6", "#ff6b81", "#fffa65"]
simbolos_flor = ["❀", "🌸", "🌻", "🌷", "🌼"]

st.title("🌷 Floralia: El Jardín de las Ideas Positivas")
st.write("Bienvenido a tu rincón de paz. Planta flores digitales y cultiva una mente llena de inspiración con textos claros y limpios.")

col1, col2 = st.columns([2, 1])

with col1:
    if st.button("🌱 Plantar una Nueva Flor", key="btn_plantar", use_container_width=True):
        nueva_flor = {
            "id": len(st.session_state.flores) + 1,
            "color": random.choice(colores_flor),
            "simbolo": random.choice(simbolos_flor),
            "frase": random.choice(frases),
            "tamanio": random.randint(35, 55)
        }
        st.session_state.flores.append(nueva_flor)
        st.toast("¡Has plantado una nueva flor con éxito!", icon="🌸")

with col2:
    st.session_state.fondo_actual = st.selectbox(
        "Estilo del Jardín", 
        list(fondos.keys()), 
        key="select_fondo"
    )

st.divider()

gradiente = fondos[st.session_state.fondo_actual]

estilo_jardin = f"""
<div style="
    background: {gradiente};
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    min-height: 380px;
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    justify-content: center;
    align-items: center;
">
"""

if not st.session_state.flores:
    estilo_jardin += """
    <div style="color: white; text-align: center; font-size: 20px; font-family: sans-serif; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">
        <p>🌿 Tu jardín está esperando su primera semilla...</p>
        <p style="font-size: 15px;">Haz clic en el botón de arriba para plantar una flor única.</p>
    </div>
    """
else:
    for flor in st.session_state.flores:
        estilo_jardin += f"""
        <div style="
            background: white;
            padding: 15px;
            border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
            text-align: center;
            width: 170px;
        ">
            <div style="font-size: {flor['tamanio']}px; color: {flor['color']}; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                {flor['simbolo']}
            </div>
            <p style="font-size: 13px; color: #333; margin-top: 10px; font-family: sans-serif; font-style: italic; line-height: 1.4;">
                &ldquo;{flor['frase']}&rdquo;
            </p>
        </div>
        """

estilo_jardin += "</div>"

st.components.v1.html(estilo_jardin, height=450)

if st.session_state.flores:
    st.write("")
    if st.button("🍂 Limpiar el Jardín", key="btn_limpiar"):
        st.session_state.flores = []
        st.rerun()
