st.title("📷 Editor de Fotos Fácil")
st.markdown(
    "Una aplicación sencilla para retocar y personalizar tus imágenes directamente desde el navegador de forma rápida."
)

if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "brightness" not in st.session_state:
    st.session_state.brightness = 100
if "contrast" not in st.session_state:
    st.session_state.contrast = 100
if "filter_type" not in st.session_state:
    st.session_state.filter_type = "Normal"
if "rotation" not in st.session_state:
    st.session_state.rotation = 0
if "custom_text" not in st.session_state:
    st.session_state.custom_text = ""
if "text_color" not in st.session_state:
    st.session_state.text_color = "#FFFFFF"

uploaded_file = st.file_uploader("Carga una imagen desde tu dispositivo", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file is not None:
    st.session_state.uploaded_image = uploaded_file

if st.session_state.uploaded_image is not None:
    st.success("¡Imagen cargada con éxito!")
    
    col_menu, col_preview = st.columns([1, 2])
    
    with col_menu:
        st.header("🎛️ Herramientas")
        
        with st.expander("Ajustes de Imagen", expanded=True):
            st.session_state.brightness = st.slider("Brillo", 0, 200, st.session_state.brightness)
            st.session_state.contrast = st.slider("Contraste", 0, 200, st.session_state.contrast)
            
        with st.expander("Filtros de Color"):
            st.session_state.filter_type = st.radio(
                "Elige un filtro",
                ["Normal", "Blanco y Negro", "Sepia", "Invertido"],
                index=["Normal", "Blanco y Negro", "Sepia", "Invertido"].index(st.session_state.filter_type)
            )
            
        with st.expander("Girar y Orientación"):
            if st.button("🔄 Girar 90° a la derecha"):
                st.session_state.rotation = (st.session_state.rotation + 90) % 360
            if st.button("🔄 Girar 90° a la izquierda"):
                st.session_state.rotation = (st.session_state.rotation - 90) % 360
                
        with st.expander("Añadir Texto"):
            st.session_state.custom_text = st.text_input("Texto personalizado", st.session_state.custom_text)
            st.session_state.text_color = st.color_picker("Color del texto", st.session_state.text_color)
            
        if st.button("🔄 Restablecer todo"):
            st.session_state.brightness = 100
            st.session_state.contrast = 100
            st.session_state.filter_type = "Normal"
            st.session_state.rotation = 0
            st.session_state.custom_text = ""
            st.session_state.text_color = "#FFFFFF"
            st.rerun()

    with col_preview:
        st.header("🖼️ Vista Previa")
        
        bytes_data = st.session_state.uploaded_image.getvalue()
        
        filter_css = f"brightness({st.session_state.brightness}%) contrast({st.session_state.contrast}%);"
        if st.session_state.filter_type == "Blanco y Negro":
            filter_css += " grayscale(100%);"
        elif st.session_state.filter_type == "Sepia":
            filter_css += " sepia(100%);"
        elif st.session_state.filter_type == "Invertido":
            filter_css += " invert(100%);"
            
        rotation_css = f"transform: rotate({st.session_state.rotation}deg);"
        
        # Mostramos la imagen usando st.image directamente con los controles de Streamlit
        st.image(st.session_state.uploaded_image, caption="Tu foto", use_container_width=True)
        
        if st.session_state.custom_text:
            st.markdown(
                f"<div style='text-align: center; color: {st.session_state.text_color}; font-size: 20px; font-weight: bold; background: rgba(0,0,0,0.6); padding: 8px; border-radius: 6px; margin-top: -40px; position: relative;'>{st.session_state.custom_text}</div>",
                unsafe_allow_html=True
            )
        
        st.info("💡 Puedes descargar tu imagen directamente con el botón de abajo.")
        
        st.markdown("### 💾 Guardar y Descargar")
        st.download_button(
            label="⬇️ Descargar Imagen",
            data=bytes_data,
            file_name="foto_editada.jpg",
            mime="image/jpeg"
        )
else:
    st.info("👈 Por favor, carga una imagen usando el botón de arriba para comenzar a editar.")
