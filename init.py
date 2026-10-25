"""Yahoraque: entry point.

Access with name + PIN, guest or admin.
"""

import logging

import streamlit as st

import analyst
import auth
import llm
import storage

ANALYST_URL_PATH = "mi-app"
ASTROS_MESSAGE = "Los astros no están alineados, inténtalo más tarde."
ROLE_LABELS = {
    auth.ROLE_GUEST: "invitado",
    auth.ROLE_USER: "usuario",
    auth.ROLE_ADMIN: "admin",
}


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
        st.page_link(my_app_page, label="Crear o cambiar mi aplicación", icon="💬")


def requirements_path(uid):
    return f"users/{uid}/requisitos.md"


def saved_requirements(uid):
    # Read once per session: in production each read is a GitHub API call.
    if "saved_requirements" not in st.session_state:
        st.session_state.saved_requirements = storage.read_file(requirements_path(uid))
    return st.session_state.saved_requirements


def show_requirements(requirements):
    with st.container(border=True):
        st.markdown(requirements.replace("\n", "  \n"))


def analyst_page():
    user = st.session_state.user
    st.title("Mi aplicación")

    saved = saved_requirements(user["id"])
    if saved:
        with st.expander("Lo que ya me pediste"):
            show_requirements(saved)

    st.session_state.setdefault("chat", [])
    st.chat_message("assistant").write(analyst.GREETING)
    for message in st.session_state.chat:
        st.chat_message(message["role"]).write(message["content"])

    pending = st.session_state.get("pending_requirements")
    if pending:
        show_requirements(pending)
        st.write("¿Empezamos a construirla?")
        yes, change = st.columns(2)
        if yes.button("¡Sí, adelante!", type="primary", width="stretch"):
            try:
                storage.write_file(
                    requirements_path(user["id"]), pending, f"Requisitos {user['id']}"
                )
            except Exception:
                logging.exception("Saving requirements failed")
                st.error("No hemos podido guardar tus requisitos. Inténtalo de nuevo en un rato.")
                return
            st.session_state.saved_requirements = pending
            st.session_state.chat = []
            del st.session_state.pending_requirements
            st.session_state.requirements_saved = True
            st.rerun()
        if change.button("Quiero cambiar algo", width="stretch"):
            del st.session_state.pending_requirements
            st.session_state.chat.append(
                {"role": "assistant", "content": "Claro, dime qué quieres cambiar."}
            )
            st.rerun()

    if st.session_state.pop("requirements_saved", False):
        st.success(
            "¡Guardado! Ya tengo todo lo necesario. "
            "La construcción automática de la aplicación llegará muy pronto."
        )

    prompt = st.chat_input("Escribe aquí…")
    if prompt:
        st.session_state.pop("pending_requirements", None)
        st.session_state.chat.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        with st.spinner("Pensando…"):
            try:
                text, requirements = analyst.reply(st.session_state.chat)
            except llm.AIUnavailable:
                st.session_state.chat.pop()
                st.error(ASTROS_MESSAGE)
                return
        st.session_state.chat.append({"role": "assistant", "content": text})
        if requirements:
            st.session_state.pending_requirements = requirements
        st.rerun()


user = st.session_state.get("user")
if user is None:
    login_page()
    st.stop()

with st.sidebar:
    st.write(f"**{user['name']}** · {ROLE_LABELS[user['role']]}")
    if st.button("Salir"):
        st.session_state.clear()
        st.rerun()

my_app_page = st.Page(analyst_page, title="Mi aplicación", url_path=ANALYST_URL_PATH)
pages = [st.Page(home_page, title="Inicio", default=True)]
if user["role"] != auth.ROLE_GUEST:
    pages.append(my_app_page)

st.navigation(pages).run()
