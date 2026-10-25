"""Yahoraque: entry point.

Access with name + PIN, guest or admin.
"""

import logging
from pathlib import Path

import streamlit as st

import analyst
import apps
import auth
import developer
import llm
import session_cookie
import storage
import waiting

ANALYST_URL_PATH = "mi-app"
USERS_URL_PATH = "usuarios"
PUBLIC_URL_PATH = "publicas"
VIEW_URL_PATH = "app"
ASTROS_MESSAGE = "Los astros no están alineados, inténtalo más tarde."
BUILD_MESSAGES = {
    "ai": ASTROS_MESSAGE,
    "failed": "No hemos conseguido que la aplicación funcione. Si tenías una, sigue la "
    "anterior. Pulsa «¡Sí, adelante!» para intentarlo otra vez o cambia algo.",
    "rejected": "No podemos construir esta aplicación porque no cumple las normas de Yahoraque.",
    "error": "No hemos podido guardar tu aplicación. Inténtalo de nuevo en un rato.",
}
LOGO = Path(__file__).parent / "assets" / "logo.png"
SIDEBAR_LOGO_WIDTH = 160
ROLE_LABELS = {
    auth.ROLE_GUEST: "invitado",
    auth.ROLE_USER: "usuario",
    auth.ROLE_ADMIN: "admin",
}


def start_session(user):
    st.session_state.user = user
    st.session_state.remember_session = True


def restored_user(browser_token):
    """The user saved in the session cookie, if it is still valid.

    Locally the server sees the cookie; on Streamlit Cloud only the browser does.
    """
    token = st.context.cookies.get(session_cookie.COOKIE_NAME) or browser_token
    if not token:
        return None
    try:
        return auth.restore_session(token)
    except Exception:
        logging.exception("Restoring session failed")
        return None


def try_access(action, *args):
    try:
        start_session(action(*args))
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
    _, center, _ = st.columns([1, 2, 1])
    center.image(LOGO, width="stretch")
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
        start_session(auth.guest())
        st.rerun()


def app_meta(uid):
    """The app's name and visibility, or None if there is no app or it cannot be read."""
    try:
        return apps.load_meta(uid)
    except Exception:
        logging.exception("Loading app data failed")
        st.error("No hemos podido cargar la aplicación. Inténtalo de nuevo en un rato.")
        return None


def home_page():
    user = st.session_state.user
    meta = app_meta(user["id"])
    if meta is None:
        # Only in the menu while there is an app, but it may have just been deleted.
        st.switch_page(my_app_page)

    st.title(meta["name"])
    change, share = st.columns(2)
    change.page_link(my_app_page, label="Cambiar mi aplicación", icon="💬")
    public = st.toggle(
        "Pública",
        value=meta["public"],
        help="Aparece en «Apps públicas» y la puede usar cualquiera, también sin cuenta.",
    )
    if public != meta["public"]:
        try:
            apps.set_public(user["id"], public)
        except Exception:
            logging.exception("Changing visibility failed")
            st.error("No hemos podido cambiarlo. Inténtalo de nuevo en un rato.")
        st.rerun()
    if meta["public"]:
        share.page_link(
            view_page, label="Enlace para compartir", icon="🔗", query_params={"app": user["id"]}
        )

    show_app(user["id"])
    delete_my_app(user["id"], meta["name"])


def delete_my_app(uid, name):
    if not st.session_state.get("confirm_delete_app"):
        if st.button("Borrar mi aplicación"):
            st.session_state.confirm_delete_app = True
            st.rerun()
        return

    st.warning(f"Se borrará **{name}** y lo que pediste. Tu cuenta sigue. No se puede deshacer.")
    yes, cancel = st.columns(2)
    if yes.button("Sí, borrar", type="primary", width="stretch"):
        try:
            apps.delete(uid)
        except Exception:
            logging.exception("Deleting app failed")
            st.error("No hemos podido borrar la aplicación. Inténtalo de nuevo en un rato.")
            return
        for key in ("confirm_delete_app", "saved_requirements", "chat", "pending_requirements"):
            st.session_state.pop(key, None)
        st.toast(f"{name} borrada.")
        st.rerun()
    if cancel.button("Cancelar", width="stretch"):
        del st.session_state.confirm_delete_app
        st.rerun()


def public_page():
    st.title("Apps públicas")
    try:
        public = apps.public_apps()
    except Exception:
        logging.exception("Listing public apps failed")
        st.error("No hemos podido cargar las aplicaciones. Inténtalo de nuevo en un rato.")
        return
    if not public:
        st.write("Todavía no hay aplicaciones públicas.")
    for app in public:
        with st.container(border=True):
            st.subheader(app["name"])
            if app["description"]:
                st.write(app["description"])
            st.page_link(view_page, label="Abrir", icon="🚀", query_params={"app": app["id"]})


def app_view_page():
    uid = st.query_params.get("app")
    try:
        allowed = bool(uid) and apps.can_view(uid, st.session_state.user)
    except Exception:
        logging.exception("Loading app data failed")
        allowed = False
    if not allowed:
        # Same message for private and missing apps, so it does not reveal which exist.
        st.title("Aplicación no disponible")
        st.write("Esta aplicación no existe o no es pública.")
        st.page_link(public_list_page, label="Ver las apps públicas", icon="🔎")
        return
    st.title(apps.load_meta(uid)["name"])
    show_app(uid)


def show_app(uid):
    """Show the user's app in a frame. Returns False if there is none."""
    try:
        if apps.load(uid) is None:
            return False
    except Exception:
        logging.exception("Loading app failed")
        st.error("No hemos podido cargar la aplicación. Inténtalo de nuevo en un rato.")
        return True
    with st.container(border=True):
        apps.show(uid)
    return True


def saved_requirements(uid):
    # Read once per session: in production each read is a GitHub API call.
    if "saved_requirements" not in st.session_state:
        st.session_state.saved_requirements = storage.read_file(apps.requirements_path(uid))
    return st.session_state.saved_requirements


def show_requirements(requirements):
    with st.container(border=True):
        st.markdown(requirements.replace("\n", "  \n"))


def build_app(uid, requirements):
    """Build and save the app; returns "ok" or a key of BUILD_MESSAGES.

    Nothing is saved unless the new app works, so the previous one stays.
    """
    try:
        meta = apps.load_meta(uid) or {}
        code, name = waiting.run(developer.build, requirements, apps.load(uid), meta.get("name"))
        apps.save(uid, code, requirements, name, meta.get("public", False))
    except llm.AIUnavailable:
        return "ai"
    except developer.BuildRejected:
        return "rejected"
    except developer.BuildFailed as error:
        logging.warning("Build for %s failed: %s", uid, error)
        return "failed"
    except Exception:
        logging.exception("Building app failed")
        return "error"
    return "ok"


def analyst_page():
    user = st.session_state.user
    saved = saved_requirements(user["id"])
    meta = app_meta(user["id"])
    st.title(f"Cambiar {meta['name']}" if meta else "Crea tu aplicación")
    if saved:
        with st.expander("Lo que ya me pediste"):
            show_requirements(saved)
    # Changes start from the app the user already has.
    current_app = {"name": meta["name"], "requirements": saved} if meta and saved else None

    st.session_state.setdefault("chat", [])
    st.chat_message("assistant").write(analyst.greeting(meta and meta["name"]))
    for message in st.session_state.chat:
        st.chat_message(message["role"]).write(message["content"])

    pending = st.session_state.get("pending_requirements")
    if pending:
        show_requirements(pending)
        st.write("¿Empezamos a construirla?")
        yes, change = st.columns(2)
        if yes.button("¡Sí, adelante!", type="primary", width="stretch"):
            st.session_state.build_result = build_app(user["id"], pending)
            if st.session_state.build_result == "ok":
                st.session_state.saved_requirements = pending
                st.session_state.chat = []
                del st.session_state.pending_requirements
            st.rerun()
        if change.button("Quiero cambiar algo", width="stretch"):
            del st.session_state.pending_requirements
            st.session_state.chat.append(
                {"role": "assistant", "content": "Claro, dime qué quieres cambiar."}
            )
            st.rerun()

    build_result = st.session_state.pop("build_result", None)
    if build_result == "ok":
        st.success(f"¡Tu aplicación {apps.load_meta(user['id'])['name']} está lista!")
        st.page_link(home, label="Ver mi aplicación", icon="🚀")
    elif build_result:
        st.error(BUILD_MESSAGES[build_result])

    if st.session_state.pop("ai_failed", False):
        st.error(ASTROS_MESSAGE)

    prompt = st.chat_input("Escribe aquí…")
    if prompt:
        st.session_state.pop("pending_requirements", None)
        st.session_state.chat.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        try:
            text, requirements = waiting.run(analyst.reply, st.session_state.chat, current_app)
        except llm.AIUnavailable:
            # Rerun so the unanswered message also disappears from the screen.
            st.session_state.chat.pop()
            st.session_state.ai_failed = True
            st.rerun()
        st.session_state.chat.append({"role": "assistant", "content": text})
        if requirements:
            st.session_state.pending_requirements = requirements
        st.rerun()


def selected_user():
    uid = st.session_state.get("selected_user")
    return next((user for user in registered_users() if user["id"] == uid), None)


def registered_users():
    try:
        return auth.list_users()
    except Exception:
        logging.exception("Listing users failed")
        return []


def users_page():
    st.title("Usuarios")
    user = selected_user()
    if user is None:
        st.write("Elige un usuario en la barra de la izquierda.")
        return

    st.header(user["name"])
    if user["created_at"]:
        st.caption(f"Registrado el {user['created_at'][:10]}")

    meta = app_meta(user["id"])
    if meta:
        st.subheader(f"Su aplicación: {meta['name']} ({'pública' if meta['public'] else 'privada'})")
    else:
        st.subheader("Su aplicación")
    if not show_app(user["id"]):
        st.write("Todavía no tiene aplicación.")
    try:
        requirements = storage.read_file(apps.requirements_path(user["id"]))
    except Exception:
        logging.exception("Reading requirements failed")
        st.error("No hemos podido leer sus requisitos. Inténtalo de nuevo en un rato.")
        requirements = None
    if requirements:
        with st.expander("Sus requisitos"):
            show_requirements(requirements)

    st.divider()
    if not st.session_state.get("confirm_delete"):
        if st.button("Borrar usuario"):
            st.session_state.confirm_delete = True
            st.rerun()
        return

    st.warning(f"Se borrará a **{user['name']}** y su aplicación. No se puede deshacer.")
    yes, cancel = st.columns(2)
    if yes.button("Sí, borrar", type="primary", width="stretch"):
        try:
            auth.delete_user(user["id"])
            apps.clear_caches()
        except Exception:
            logging.exception("Deleting user failed")
            st.error("No hemos podido borrar el usuario. Inténtalo de nuevo en un rato.")
            return
        del st.session_state.selected_user
        del st.session_state.confirm_delete
        st.toast(f"{user['name']} borrado.")
        st.rerun()
    if cancel.button("Cancelar", width="stretch"):
        del st.session_state.confirm_delete
        st.rerun()


def users_sidebar():
    st.subheader("Usuarios registrados")
    users = registered_users()
    if not users:
        st.caption("Todavía no hay nadie.")
    for registered in users:
        is_selected = registered["id"] == st.session_state.get("selected_user")
        if st.button(
            registered["name"],
            key=f"user_{registered['id']}",
            type="primary" if is_selected else "secondary",
            width="stretch",
        ):
            st.session_state.selected_user = registered["id"]
            st.session_state.pop("confirm_delete", None)
            st.switch_page(admin_users_page)


user = st.session_state.get("user")
logged_out = st.session_state.get("logged_out")
if user and st.session_state.pop("remember_session", False):
    browser_token = session_cookie.sync(
        "set", auth.session_token(user), auth.SESSION_DAYS * 24 * 60 * 60
    )
elif user is None and logged_out:
    browser_token = session_cookie.sync("clear")
else:
    browser_token = session_cookie.sync()

# After "Salir" the old cookie may still be in this connection's headers: ignore it.
if user is None and not logged_out:
    user = restored_user(browser_token)
    if user:
        st.session_state.user = user
if user is None:
    login_page()
    st.stop()

is_guest = user["role"] == auth.ROLE_GUEST
my_app = None if is_guest else app_meta(user["id"])
# With an app, the menu starts with its name and opens it; without one,
# "Inicio" goes straight to the chat to create it.
home = st.Page(
    home_page, title=my_app["name"] if my_app else "Inicio", default=bool(my_app)
)
my_app_page = st.Page(
    analyst_page,
    title="Cambiar mi aplicación" if my_app else "Inicio",
    url_path=ANALYST_URL_PATH,
    default=not is_guest and not my_app,
)
public_list_page = st.Page(
    public_page, title="Apps públicas", url_path=PUBLIC_URL_PATH, default=is_guest
)
# Opened from links with ?app=<user id>, not from the menu.
view_page = st.Page(
    app_view_page, title="Aplicación", url_path=VIEW_URL_PATH, visibility="hidden"
)
admin_users_page = st.Page(users_page, title="Usuarios", url_path=USERS_URL_PATH)
if is_guest:
    pages = [public_list_page, view_page]
elif my_app:
    pages = [home, my_app_page, public_list_page, view_page]
else:
    pages = [my_app_page, public_list_page, view_page]
if user["role"] == auth.ROLE_ADMIN:
    pages.append(admin_users_page)
# Reached from links, not from the menu: an app's page, and the chat to change
# your app (its link is on the app's page).
off_menu = [view_page, my_app_page] if my_app else [view_page]
# Our own menu, so the logo can go above it at a readable size
# (st.logo is at most 32px high).
navigation = st.navigation(pages, position="hidden")

# After st.navigation, so the links and user buttons can switch page.
with st.sidebar:
    st.image(LOGO, width=SIDEBAR_LOGO_WIDTH)
    for page in pages:
        if not any(page is hidden for hidden in off_menu):
            st.page_link(page)
    st.divider()
    st.write(f"**{user['name']}** · {ROLE_LABELS[user['role']]}")
    if st.button("Salir"):
        st.session_state.clear()
        st.session_state.logged_out = True
        st.rerun()
    if user["role"] == auth.ROLE_ADMIN:
        st.divider()
        users_sidebar()

navigation.run()
