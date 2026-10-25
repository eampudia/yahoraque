st.title("🐮 Calculadora Manga Cuqui 🌸")
st.markdown(
    """
    <div style="text-align: center; background-color: #ffe6f0; padding: 15px; border-radius: 15px; border: 2px dashed #ff99cc;">
        <span style="font-size: 24px;">✨ ¡Muuuys buenos días! ¡A calcular con nuestra vaquita kawaii! ✨</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")

if "calc_display" not in st.session_state:
    st.session_state.calc_display = "0"
if "calc_op" not in st.session_state:
    st.session_state.calc_op = None
if "calc_prev" not in st.session_state:
    st.session_state.calc_prev = None
if "calc_new_num" not in st.session_state:
    st.session_state.calc_new_num = True

col_personaje, col_calc = st.columns([1, 2], gap="medium")

with col_personaje:
    st.markdown("### 🐮 Vaquita Kawaii")
    st.image("https://images.unsplash.com/photo-1527153857715-3908f2ae5e61?w=300&auto=format&fit=crop&q=80", width=180)
    st.markdown(
        """
        <div style="background-color: #fff0f5; padding: 10px; border-radius: 10px; text-align: center; border: 1px solid #ffb6c1;">
            <p style="color: #d1477a; margin: 0; font-size: 14px;"><b>¡Lola la vaquita te acompaña!</b><br>¡Muuuuchos éxitos con tus números, nya~!</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_calc:
    st.markdown(
        f"""
        <div style="background-color: #2b1d3a; color: #ffb3d9; padding: 20px; border-radius: 15px; text-align: right; font-family: monospace; font-size: 32px; border: 4px solid #ff99cc; box-shadow: 0px 4px 10px rgba(255, 153, 204, 0.4);">
            {st.session_state.calc_display}
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.write("")

    def agregar_digito(digito):
        if st.session_state.calc_new_num or st.session_state.calc_display == "0":
            st.session_state.calc_display = str(digito)
            st.session_state.calc_new_num = False
        else:
            st.session_state.calc_display += str(digito)

    def agregar_punto():
        if st.session_state.calc_new_num:
            st.session_state.calc_display = "0."
            st.session_state.calc_new_num = False
        elif "." not in st.session_state.calc_display:
            st.session_state.calc_display += "."

    def limpiar():
        st.session_state.calc_display = "0"
        st.session_state.calc_op = None
        st.session_state.calc_prev = None
        st.session_state.calc_new_num = True

    def establecer_operacion(op):
        try:
            st.session_state.calc_prev = float(st.session_state.calc_display)
        except ValueError:
            st.session_state.calc_prev = 0.0
        st.session_state.calc_op = op
        st.session_state.calc_new_num = True

    def calcular():
        if st.session_state.calc_op is not None and st.session_state.calc_prev is not None:
            try:
                actual = float(st.session_state.calc_display)
                previo = st.session_state.calc_prev
                resultado = 0.0
                
                if st.session_state.calc_op == "+":
                    resultado = previo + actual
                elif st.session_state.calc_op == "-":
                    resultado = previo - actual
                elif st.session_state.calc_op == "*":
                    resultado = previo * actual
                elif st.session_state.calc_op == "/":
                    if actual == 0:
                        st.error("¡Muuu error! No se puede dividir entre cero 🌸")
                        return
                    else:
                        resultado = previo / actual
                
                if resultado.is_integer():
                    st.session_state.calc_display = str(int(resultado))
                else:
                    st.session_state.calc_display = str(round(resultado, 6))
                
                st.session_state.calc_op = None
                st.session_state.calc_prev = None
                st.session_state.calc_new_num = True
            except ValueError:
                st.error("¡Ups! Algo salió mal con los números.")

    def calcular_porcentaje():
        try:
            actual = float(st.session_state.calc_display)
            resultado = actual / 100.0
            if resultado.is_integer():
                st.session_state.calc_display = str(int(resultado))
            else:
                st.session_state.calc_display = str(round(resultado, 6))
            st.session_state.calc_new_num = True
        except ValueError:
            st.error("¡Valor inválido para porcentaje!")

    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    with r1c1:
        if st.button("AC", key="btn_ac", use_container_width=True):
            limpiar()
    with r1c2:
        if st.button("%", key="btn_pct", use_container_width=True):
            calcular_porcentaje()
    with r1c3:
        if st.button("÷", key="btn_div", use_container_width=True):
            establecer_operacion("/")
    with r1c4:
        if st.button("×", key="btn_mul", use_container_width=True):
            establecer_operacion("*")

    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    with r2c1:
        if st.button("7", key="btn_7", use_container_width=True):
            agregar_digito(7)
    with r2c2:
        if st.button("8", key="btn_8", use_container_width=True):
            agregar_digito(8)
    with r2c3:
        if st.button("9", key="btn_9", use_container_width=True):
            agregar_digito(9)
    with r2c4:
        if st.button("-", key="btn_res", use_container_width=True):
            establecer_operacion("-")

    r3c1, r3c2, r3c3, r3c4 = st.columns(4)
    with r3c1:
        if st.button("4", key="btn_4", use_container_width=True):
            agregar_digito(4)
    with r3c2:
        if st.button("5", key="btn_5", use_container_width=True):
            agregar_digito(5)
    with r3c3:
        if st.button("6", key="btn_6", use_container_width=True):
            agregar_digito(6)
    with r3c4:
        if st.button("+", key="btn_sum", use_container_width=True):
            establecer_operacion("+")

    r4c1, r4c2, r4c3, r4c4 = st.columns(4)
    with r4c1:
        if st.button("1", key="btn_1", use_container_width=True):
            agregar_digito(1)
    with r4c2:
        if st.button("2", key="btn_2", use_container_width=True):
            agregar_digito(2)
    with r4c3:
        if st.button("3", key="btn_3", use_container_width=True):
            agregar_digito(3)
    with r4c4:
        if st.button("=", key="btn_igual", use_container_width=True):
            calcular()

    r5c1, r5c2, r5c3 = st.columns([2, 1, 1])
    with r5c1:
        if st.button("0", key="btn_0", use_container_width=True):
            agregar_digito(0)
    with r5c2:
        if st.button(".", key="btn_punto", use_container_width=True):
            agregar_punto()
    with r5c3:
        if st.button("💖", key="btn_heart", use_container_width=True):
            st.balloons()
            st.toast("¡Lola te manda un muuuuy fuerte abrazo! 💕")

st.markdown("---")
st.caption("Calculadora Manga Cuqui • Con vaquita kawaii y estética pastel 🌸")
