"""Yahoraque: entry point.

Access with name + PIN, guest or admin. The phase 0 spike (push to master
and apps stored as text) is kept as an admin-only page.
"""

import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

import auth
import storage

ROOT = Path(__file__).parent
APPS_DIR = ROOT / "spike_apps"
PUSH_TEST_PATH = "spike/push_test.txt"
SECRET_NAMES = [
    "GOOGLE_API_KEY",
    "GITHUB_TOKEN",
    "GITHUB_REPO",
    "ADMIN_NAME",
    "ADMIN_PASSWORD",
    "PIN_SECRET",
    "STORAGE_MODE",
]
ROLE_LABELS = {
    auth.ROLE_GUEST: "invitado",
    auth.ROLE_USER: "usuario",
    auth.ROLE_ADMIN: "admin",
}


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


@st.cache_resource
def server_started_at():
    # Cached once per server process: if this changes, the server restarted.
    return now()


def try_access(action, *args):
    try:
        st.session_state.user = action(*args)
    except auth.LoginError as error:
        st.error(str(error))
        return
    except Exception:
        # The user sees a friendly message; the real cause goes to the logs.
        logging.exception("Access failed")
        st.error("No hemos podido comprobar tus datos. Inténtalo de nuevo en un rato.")
        return
    st.rerun()


def login_page():
    st.title("Yahoraque")
    st.write("Crea tu propia aplicación sin saber programar.")

    enter_tab, new_tab = st.tabs(["Entrar", "Soy nuevo"])
    with enter_tab:
        with st.form("login"):
            name = st.text_input("Tu nombre")
            pin = st.text_input("Tu PIN", type="password")
            if st.form_submit_button("Entrar"):
                try_access(auth.login, name, pin)

    with new_tab:
        with st.form("register"):
            name = st.text_input("Elige un nombre")
            pin = st.text_input("Elige un PIN (de 4 a 8 números)", type="password")
            pin_again = st.text_input("Repite el PIN", type="password")
            st.caption(
                "Te recomendamos usar un alias en lugar de tu nombre real. "
                "Si olvidas el PIN no se puede recuperar."
            )
            if st.form_submit_button("Crear mi usuario"):
                if pin != pin_again:
                    st.error("Los dos PIN no coinciden.")
                else:
                    try_access(auth.register, name, pin)

    st.divider()
    if st.button("Entrar como invitado"):
        st.session_state.user = auth.guest()
        st.rerun()


def home_page():
    user = st.session_state.user
    st.title("Yahoraque")
    if user["role"] == auth.ROLE_GUEST:
        st.write("Aquí verás el listado de aplicaciones públicas.")
    else:
        st.write(f"Hola, {user['name']}. Aquí verás tu aplicación.")


def spike_page():
    st.title("Prueba técnica (fase 0)")

    st.header("0. Secretos configurados")
    for name in SECRET_NAMES:
        st.write("✅" if storage.get_secret(name) else "❌", f"`{name}`")

    st.header("1. ¿Qué pasa al hacer push a master?")
    st.session_state.setdefault("session_started_at", now())
    st.session_state.setdefault("clicks", 0)

    disk_file = ROOT / PUSH_TEST_PATH
    col1, col2, col3 = st.columns(3)
    col1.metric("Servidor arrancado", server_started_at())
    col2.metric("Sesión iniciada", st.session_state.session_started_at)
    col3.metric("Clics en esta sesión", st.session_state.clicks)
    st.write(
        "Contenido en disco de",
        f"`{PUSH_TEST_PATH}`:",
        disk_file.read_text() if disk_file.exists() else "(no existe)",
    )

    if st.button("Sumar un clic"):
        st.session_state.clicks += 1
        st.rerun()

    if st.button("Hacer push de prueba a master"):
        try:
            sha = storage.push_file(PUSH_TEST_PATH, f"push {now()}\n", "spike: push test")
            st.success(f"Push hecho. Commit {sha[:7]}.")
        except Exception as error:
            st.error(f"El push ha fallado: {error}")

    st.header("2. Crear una app guardada como texto")
    with st.form("new_app"):
        name = st.text_input("Nombre del usuario", value="prueba")
        code = st.text_area(
            "Código de la app",
            value='st.title("Hola")\nst.write("Soy una app generada.")',
            height=150,
        )
        push = st.checkbox("Subirla también a GitHub")
        if st.form_submit_button("Guardar app"):
            app_id = hashlib.sha256(name.strip().lower().encode()).hexdigest()[:12]
            APPS_DIR.mkdir(exist_ok=True)
            (APPS_DIR / f"{app_id}.py").write_text(code)
            if push:
                try:
                    storage.push_file(f"spike_apps/{app_id}.py", code, f"spike: app {app_id}")
                except Exception as error:
                    st.error(f"El push ha fallado: {error}")
            st.session_state.saved_app = app_id
            st.rerun()

    if "saved_app" in st.session_state:
        st.success(f"App guardada en la ruta `/{st.session_state.saved_app}`.")


def make_app_page(path):
    def run_app():
        code = path.read_text()
        exec(compile(code, str(path), "exec"), {"st": st, "__name__": "__app__"})

    return run_app


user = st.session_state.get("user")
if user is None:
    login_page()
    st.stop()

with st.sidebar:
    st.write(f"**{user['name']}** · {ROLE_LABELS[user['role']]}")
    if st.button("Salir"):
        st.session_state.clear()
        st.rerun()

pages = [st.Page(home_page, title="Inicio", default=True)]
if user["role"] == auth.ROLE_ADMIN:
    pages.append(st.Page(spike_page, title="Prueba técnica", url_path="prueba"))
for app_file in sorted(APPS_DIR.glob("*.py")):
    pages.append(
        st.Page(make_app_page(app_file), title=app_file.stem, url_path=app_file.stem)
    )

st.navigation(pages).run()
