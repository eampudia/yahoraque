import random

st.title("📸 Mi Mini Editor de Fotos")
st.markdown("Sube una imagen, dale tu toque personal con filtros, brillo, contraste y texto, ¡y descárgala al instante!")

# Inicializar estado
if "imagen_cargada" not in st.session_state:
    st.session_state.imagen_cargada = None

# Sección de subida de archivo
archivo_subido = st.file_uploader("Sube una imagen (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"], key="uploader_foto")

if archivo_subido is not None:
    st.session_state.imagen_cargada = archivo_subido

if st.session_state.imagen_cargada is not None:
    # Creamos dos columnas: izquierda para controles, derecha para la vista previa
    col_controles, col_preview = st.columns([1, 2], gap="large")

    with col_controles:
        st.subheader("🛠️ Controles")
        
        # Ajustes básicos
        st.markdown("**Ajustes de imagen**")
        brillo = st.slider("Brillo", 50, 150, 100, 5, key="slider_brillo", help="Porcentaje de brillo")
        contraste = st.slider("Contraste", 50, 150, 100, 5, key="slider_contraste", help="Porcentaje de contraste")
        
        # Filtros de color
        st.markdown("**Filtros**")
        filtro = st.selectbox(
            "Elige un filtro",
            ["Normal", "Escala de grises", "Sepia (Tono cálido)", "Invertido"],
            key="select_filtro"
        )
        
        # Texto personalizado
        st.markdown("**Añadir Texto**")
        texto_usuario = st.text_input("Texto sobre la imagen", "", key="input_texto")
        color_texto = st.color_picker("Color del texto", "#FFFFFF", key="color_texto")
        tamano_texto = st.slider("Tamaño del texto (px)", 12, 72, 24, key="slider_tamano")
        
        # Icono / Emoji decorativo
        st.markdown("**Añadir Sello / Emoji**")
        emoji_elegido = st.selectbox(
            "Elige un sello",
            ["⭐ Estrellita", "❤️ Corazón", "🔥 Fuego", "😎 Gafas", "🐱 Gato", "🚀 Cohete", "Ninguno"],
            key="select_emoji"
        )

    with col_preview:
        st.subheader("✨ Vista Previa")
        
        bytes_imagen = st.session_state.imagen_cargada.getvalue()
        tipo_mime = st.session_state.imagen_cargada.type
        
        # Codificación manual a base64 usando bloques de 3 bytes (sin importar módulos prohibidos)
        caracteres_b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
        
        def codificar_a_base64(datos):
            resultado = []
            longitud = len(datos)
            for i in range(0, longitud, 3):
                bloque = datos[i:i+3]
                b = len(bloque)
                
                val = 0
                for j in range(b):
                    val += bloque[j] << (8 * (2 - j))
                
                for j in range(4):
                    if j > b:
                        resultado.append("=")
                    else:
                        indice = (val >> (6 * (3 - j))) & 63
                        resultado.append(caracteres_b64[indice])
                        
            return "".join(resultado)

        base64_img = codificar_a_base64(bytes_imagen)
        src_data = f"data:{tipo_mime};base64,{base64_img}"
        
        # Mapeo de filtros a CSS filters
        filtro_css = "none"
        if filtro == "Escala de grises":
            filtro_css = "grayscale(100%)"
        elif filtro == "Sepia (Tono cálido)":
            filtro_css = "sepia(100%)"
        elif filtro == "Invertido":
            filtro_css = "invert(100%)"
            
        brillo_css = brillo / 100.0
        contraste_css = contraste / 100.0
        
        # Extraer emoji limpio
        emoji_map = {
            "⭐ Estrellita": "⭐",
            "❤️ Corazón": "❤️",
            "🔥 Fuego": "🔥",
            "😎 Gafas": "😎",
            "🐱 Gato": "🐱",
            "🚀 Cohete": "🚀",
            "Ninguno": ""
        }
        emoji_char = emoji_map.get(emoji_elegido, "")
        
        # Construir HTML para simular la edición visual interactiva
        html_editor = f"""
        <div style="
            position: relative; 
            display: inline-block; 
            max-width: 100%; 
            background: #111; 
            border-radius: 12px; 
            overflow: hidden; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            text-align: center;
        ">
            <img src="{src_data}" style="
                display: block; 
                max-width: 100%; 
                height: auto; 
                filter: brightness({brillo_css}) contrast({contraste_css}) {filtro_css};
                transition: filter 0.2s ease;
            ">
            <div style="
                position: absolute; 
                bottom: 20px; 
                left: 50%; 
                transform: translateX(-50%); 
                color: {color_texto}; 
                font-size: {tamano_texto}px; 
                font-weight: bold; 
                text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
                width: 90%;
                word-break: break-word;
                pointer-events: none;
                font-family: sans-serif;
            ">{texto_usuario}</div>
            
            <div style="
                position: absolute; 
                top: 20px; 
                right: 20px; 
                font-size: {int(tamano_texto * 1.5)}px; 
                pointer-events: none;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
            ">{emoji_char}</div>
        </div>
        """
        
        st.components.v1.html(html_editor, height=450)
        
        st.info("💡 Consejo: Los ajustes se aplican en tiempo real en la vista previa. Cuando estés listo, puedes descargar tu imagen original o reiniciar.")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            st.download_button(
                "📥 Descargar Imagen Original",
                data=bytes_imagen,
                file_name="foto_original.jpg",
                mime=tipo_mime,
                key="btn_descargar_orig"
            )
        with col_btn2:
            if st.button("🗑️ Cambiar de imagen", key="btn_reset"):
                st.session_state.imagen_cargada = None
                st.rerun()

else:
    # Estado inicial: Pantalla vacía con invitación a subir
    st.markdown("""
    <div style="
        border: 2px dashed #ccc; 
        border-radius: 15px; 
        padding: 40px; 
        text-align: center; 
        background: #f9f9f9;
        margin-top: 20px;
    ">
        <h3 style="color: #666; margin-bottom: 10px;">¡Sube una foto para empezar a editar!</h3>
        <p style="color: #888; font-size: 14px;">Puedes añadir brillo, contraste, filtros divertidos y textos personalizados en segundos.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    st.subheader("O prueba con esta imagen de ejemplo:")
    if st.button("Cargar foto de ejemplo", key="btn_ejemplo"):
        st.info("Para usar una imagen de ejemplo, por favor sube cualquier foto desde tu dispositivo usando el selector superior.")
