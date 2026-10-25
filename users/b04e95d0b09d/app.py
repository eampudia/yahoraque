st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bangers&family=Permanent+Marker&display=swap');

    .manga-container {
        background-color: #ffffff;
        border: 4px solid #000000;
        box-shadow: 6px 6px 0px #85bb65;
        padding: 20px;
        border-radius: 12px;
        max-width: 400px;
        margin: 0 auto;
        font-family: 'Permanent Marker', cursive;
    }

    .manga-title {
        font-family: 'Bangers', cursive;
        font-size: 38px;
        color: #000000;
        text-align: center;
        letter-spacing: 2px;
        text-shadow: 2px 2px 0px #85bb65;
        margin-bottom: 15px;
    }

    .manga-screen {
        background-color: #f4fff0;
        border: 3px solid #000000;
        box-shadow: inset 3px 3px 0px rgba(0,0,0,0.1);
        padding: 15px;
        font-size: 32px;
        text-align: right;
        margin-bottom: 20px;
        border-radius: 8px;
        color: #1a3300;
        font-family: 'Bangers', cursive;
        letter-spacing: 1px;
    }

    .kiwi-badge {
        background-color: #85bb65;
        color: white;
        border: 2px solid black;
        padding: 2px 8px;
        font-size: 14px;
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 10px;
        font-family: 'Permanent Marker', cursive;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if "pantalla" not in st.session_state:
    st.session_state.pantalla = "0"
if "nuevo_numero" not in st.session_state:
    st.session_state.nuevo_numero = True

def agregar(digito):
    if st.session_state.pantalla == "0" or st.session_state.nuevo_numero:
        st.session_state.pantalla = str(digito)
        st.session_state.nuevo_numero = False
    else:
        st.session_state.pantalla += str(digito)

def limpiar():
    st.session_state.pantalla = "0"
    st.session_state.nuevo_numero = True

def operador(op):
    st.session_state.pantalla += f" {op} "
    st.session_state.nuevo_numero = False

def calcular():
    try:
        partes = st.session_state.pantalla.split()
        if len(partes) >= 3:
            num1 = float(partes[0])
            op = partes[1]
            num2 = float(partes[2])
            
            if op == "+":
                resultado = num1 + num2
            elif op == "-":
                resultado = num1 - num2
            elif op == "×":
                resultado = num1 * num2
            elif op == "÷":
                if num2 == 0:
                    st.session_state.pantalla = "¡Zas! Error"
                    st.session_state.nuevo_numero = True
                    return
                resultado = num1 / num2
            else:
                resultado = num2
                
            if isinstance(resultado, float) and resultado.is_integer():
                resultado = int(resultado)
            st.session_state.pantalla = str(resultado)
            st.session_state.nuevo_numero = True
    except:
        st.session_state.pantalla = "¡Zas! Error"
        st.session_state.nuevo_numero = True

def porcentaje():
    try:
        parts = st.session_state.pantalla.split()
        if len(parts) == 1:
            val = float(parts[0]) / 100
            st.session_state.pantalla = str(val if not val.is_integer() else int(val))
            st.session_state.nuevo_numero = True
    except:
        st.session_state.pantalla = "¡Zas! Error"
        st.session_state.nuevo_numero = True

st.markdown('<div class="manga-container">', unsafe_allow_html=True)
st.markdown('<div class="manga-title">🥝 CALCULADORA MANGA KIWI 🥝</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center;"><span class="kiwi-badge">¡Poderes dulces y ácidos!</span></div>', unsafe_allow_html=True)

st.markdown(f'<div class="manga-screen">{st.session_state.pantalla}</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("C", key="btn_c", use_container_width=True):
        limpiar()
with col2:
    if st.button("%", key="btn_porc", use_container_width=True):
        porcentaje()
with col3:
    if st.button("÷", key="btn_div", use_container_width=True):
        operador("÷")
with col4:
    if st.button("×", key="btn_mult", use_container_width=True):
        operador("×")

c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("7", key="btn_7", use_container_width=True):
        agregar(7)
with c2:
    if st.button("8", key="btn_8", use_container_width=True):
        agregar(8)
with c3:
    if st.button("9", key="btn_9", use_container_width=True):
        agregar(9)
with c4:
    if st.button("-", key="btn_menos", use_container_width=True):
        operador("-")

c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("4", key="btn_4", use_container_width=True):
        agregar(4)
with c2:
    if st.button("5", key="btn_5", use_container_width=True):
        agregar(5)
with c3:
    if st.button("6", key="btn_6", use_container_width=True):
        agregar(6)
with c4:
    if st.button("+", key="btn_mas", use_container_width=True):
        operador("+")

c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("1", key="btn_1", use_container_width=True):
        agregar(1)
with c2:
    if st.button("2", key="btn_2", use_container_width=True):
        agregar(2)
with c3:
    if st.button("3", key="btn_3", use_container_width=True):
        agregar(3)
with c4:
    if st.button("=", key="btn_igual", use_container_width=True):
        calcular()

c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("0", key="btn_0", use_container_width=True):
        agregar(0)
with c2:
    if st.button(".", key="btn_punto", use_container_width=True):
        agregar(".")
with c3:
    st.write("")
with c4:
    st.write("")

st.markdown('</div>', unsafe_allow_html=True)
