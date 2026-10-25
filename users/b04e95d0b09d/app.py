st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600&family=Permanent+Marker&display=swap');

    .manga-container {
        background: linear-gradient(135deg, #fff0f5 0%, #f0f8ff 100%);
        border: 4px solid #ffb6c1;
        box-shadow: 6px 6px 0px #dda0dd;
        padding: 25px;
        border-radius: 20px;
        max-width: 420px;
        margin: 0 auto;
        font-family: 'Fredoka', sans-serif;
    }

    .manga-title {
        font-family: 'Permanent Marker', cursive;
        font-size: 34px;
        color: #db7093;
        text-align: center;
        letter-spacing: 2px;
        text-shadow: 2px 2px 0px #e6e6fa;
        margin-bottom: 5px;
    }

    .manga-subtitle {
        text-align: center;
        color: #9370db;
        font-size: 15px;
        font-weight: 600;
        margin-bottom: 20px;
    }

    .manga-screen {
        background-color: #ffffff;
        border: 3px solid #dda0dd;
        box-shadow: inset 3px 3px 0px rgba(221, 160, 221, 0.2);
        padding: 15px;
        font-size: 36px;
        text-align: right;
        margin-bottom: 20px;
        border-radius: 12px;
        color: #4a4a4a;
        font-family: 'Fredoka', sans-serif;
        font-weight: 600;
        letter-spacing: 1px;
        min-height: 70px;
        word-break: break-all;
    }

    .memory-indicator {
        font-size: 14px;
        color: #ff69b4;
        font-weight: 600;
        margin-bottom: 8px;
        min-height: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if "pantalla" not in st.session_state:
    st.session_state.pantalla = "0"
if "nuevo_numero" not in st.session_state:
    st.session_state.nuevo_numero = True
if "memoria" not in st.session_state:
    st.session_state.memoria = 0.0

def agregar(digito):
    digito_str = str(digito)
    if st.session_state.pantalla == "0" or st.session_state.nuevo_numero:
        if digito_str == ".":
            st.session_state.pantalla = "0."
        else:
            st.session_state.pantalla = digito_str
        st.session_state.nuevo_numero = False
    else:
        if digito_str == "." and "." in st.session_state.pantalla:
            return
        st.session_state.pantalla += digito_str

def limpiar():
    st.session_state.pantalla = "0"
    st.session_state.nuevo_numero = True

def operador(op):
    try:
        val = st.session_state.pantalla.rstrip(" +-*/")
        st.session_state.pantalla = f"{val} {op} "
        st.session_state.nuevo_numero = False
    except:
        st.session_state.pantalla = "¡UwU! Error"
        st.session_state.nuevo_numero = True

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
                    st.session_state.pantalla = "¡Ay no! Cero"
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
        st.session_state.pantalla = "¡UwU! Error"
        st.session_state.nuevo_numero = True

def porcentaje():
    try:
        val = float(st.session_state.pantalla) / 100
        if val.is_integer():
            val = int(val)
        st.session_state.pantalla = str(val)
        st.session_state.nuevo_numero = True
    except:
        st.session_state.pantalla = "¡UwU! Error"
        st.session_state.nuevo_numero = True

def usar_memoria(accion):
    try:
        actual = float(st.session_state.pantalla)
        if accion == "M+":
            st.session_state.memoria += actual
        elif accion == "M-":
            st.session_state.memoria -= actual
        elif accion == "MR":
            val = st.session_state.memoria
            if val.is_integer():
                val = int(val)
            st.session_state.pantalla = str(val)
            st.session_state.nuevo_numero = True
        elif accion == "MC":
            st.session_state.memoria = 0.0
    except:
        pass

st.markdown('<div class="manga-container">', unsafe_allow_html=True)
st.markdown('<div class="manga-title">🌸 MANGA PASTEL 🌸</div>', unsafe_allow_html=True)
st.markdown('<div class="manga-subtitle">✨ ¡Calculadora mágica y cuqui! ✨</div>', unsafe_allow_html=True)

mem_text = f"💖 Memoria: {int(st.session_state.memoria) if float(st.session_state.memoria).is_integer() else st.session_state.memoria}" if st.session_state.memoria != 0 else ""
st.markdown(f'<div class="memory-indicator">{mem_text}</div>', unsafe_allow_html=True)

st.markdown(f'<div class="manga-screen">{st.session_state.pantalla}</div>', unsafe_allow_html=True)

# Fila de Memoria y Funciones Especiales
col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
with col_m1:
    if st.button("MC", key="btn_mc", use_container_width=True):
        usar_memoria("MC")
with col_m2:
    if st.button("MR", key="btn_mr", use_container_width=True):
        usar_memoria("MR")
with col_m3:
    if st.button("M+", key="btn_mplus", use_container_width=True):
        usar_memoria("M+")
with col_m4:
    if st.button("M-", key="btn_mmin", use_container_width=True):
        usar_memoria("M-")
with col_m5:
    if st.button("%", key="btn_porc", use_container_width=True):
        porcentaje()

# Fila 1: C, División, Multiplicación
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("C", key="btn_c", use_container_width=True):
        limpiar()
with col2:
    if st.button("←", key="btn_del", use_container_width=True):
        if len(st.session_state.pantalla) > 1 and not st.session_state.nuevo_numero:
            st.session_state.pantalla = st.session_state.pantalla[:-1]
        else:
            st.session_state.pantalla = "0"
            st.session_state.nuevo_numero = True
with col3:
    if st.button("÷", key="btn_div", use_container_width=True):
        operador("÷")
with col4:
    if st.button("×", key="btn_mult", use_container_width=True):
        operador("×")

# Fila 2: 7, 8, 9, Resta
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("7", key="btn_7", use_container_width=True):
        agregar(7)
with col2:
    if st.button("8", key="btn_8", use_container_width=True):
        agregar(8)
with col3:
    if st.button("9", key="btn_9", use_container_width=True):
        agregar(9)
with col4:
    if st.button("-", key="btn_menos", use_container_width=True):
        operador("-")

# Fila 3: 4, 5, 6, Suma
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("4", key="btn_4", use_container_width=True):
        agregar(4)
with col2:
    if st.button("5", key="btn_5", use_container_width=True):
        agregar(5)
with col3:
    if st.button("6", key="btn_6", use_container_width=True):
        agregar(6)
with col4:
    if st.button("+", key="btn_mas", use_container_width=True):
        operador("+")

# Fila 4: 1, 2, 3, Igual
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("1", key="btn_1", use_container_width=True):
        agregar(1)
with col2:
    if st.button("2", key="btn_2", use_container_width=True):
        agregar(2)
with col3:
    if st.button("3", key="btn_3", use_container_width=True):
        agregar(3)
with col4:
    if st.button("=", key="btn_igual", use_container_width=True):
        calcular()

# Fila 5: 0, Punto
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("0", key="btn_0", use_container_width=True):
        agregar(0)
with col2:
    if st.button(".", key="btn_punto", use_container_width=True):
        agregar(".")
with col3:
    st.write("")
with col4:
    st.write("")

st.markdown('</div>', unsafe_allow_html=True)
