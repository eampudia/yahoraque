"""Yahoraque: entry point.

Access with name + PIN, guest or admin.
"""

import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

import streamlit as st

import analyst
import app_ai
import apps
import auth
import developer
import llm
import session_cookie
import storage
import usage
import waiting

ANALYST_URL_PATH = "mi-app"
USERS_URL_PATH = "usuarios"
PUBLIC_URL_PATH = "publicas"
VIEW_URL_PATH = "app"
USAGE_URL_PATH = "consumo"
AI_STUDIO_USAGE_URL = "https://aistudio.google.com/usage"
# Days shown in the admin's "Consumo" page, besides today.
PAST_DAYS = 14
ASTROS_MESSAGE = "Los astros no están alineados, inténtalo más tarde."
# Always under the analyst's chat.
AI_DISCLAIMER = (
    "El analista es una inteligencia artificial y puede cometer errores. "
    "Revisa los requisitos antes de confirmar la construcción."
)
SAVED_NOTICE = (
    "Tu aplicación y sus versiones se guardan: las encontrarás aquí la próxima vez que entres."
)
BUILDS_PER_DAY = 10
BUILD_MESSAGES = {
    "ai": ASTROS_MESSAGE,
    "failed": "No hemos conseguido que la aplicación funcione. Si tenías una, sigue la "
    "anterior. Pulsa «¡Sí, adelante!» para intentarlo otra vez o cambia algo.",
    "rejected": "No podemos construir esta aplicación porque no cumple las normas de Yahoraque.",
    "error": "No hemos podido guardar tu aplicación. Inténtalo de nuevo en un rato.",
    "limit": f"Hoy ya has construido tu aplicación {BUILDS_PER_DAY} veces, que es el máximo "
    "del día. Vuelve a intentarlo mañana.",
}
# The labels the analyst writes in the requirements, shown in bold.
REQUIREMENT_LABEL = re.compile(r"^([A-ZÁÉÍÓÚ][^:\n]{1,30}):")
# Ideas for an empty chat, from a teacher's day to day: (button, first message).
EXAMPLE_IDEAS = [
    (
        "📝 Corregir redacciones de idiomas",
        "Soy profesor de francés. Quiero una app para corregir las redacciones de mis alumnos: "
        "pegar el texto o subir una foto, elegir el nivel y ver una nota sobre 10 con los errores "
        "explicados.",
    ),
    (
        "🎲 Hacer grupos al azar",
        "Quiero una app para hacer grupos al azar con los nombres de mis alumnos, eligiendo "
        "cuántos alumnos hay en cada grupo.",
    ),
    (
        "❓ Un juego de preguntas para repasar",
        "Quiero un juego de preguntas tipo concurso para repasar un tema en clase, con "
        "puntuación y un temporizador.",
    ),
    (
        "🧮 Calcular la nota media",
        "Quiero una app para calcular la nota final de un alumno a partir de las notas de "
        "exámenes, trabajos y actitud, cada una con su porcentaje.",
    ),
]
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
    ai_badge(meta)
    st.page_link(my_app_page, label="Cambiar mi aplicación", icon=":material/edit:")
    public_toggle(user["id"], meta)
    if meta["public"]:
        st.caption(":material/share: Enlace para compartir (pulsa el icono de copiar):")
        st.code(share_url(user["id"], meta), language=None)

    show_app(user["id"], meta)
    # A classmate missed persistence because nothing on screen showed it.
    st.caption(f":material/cloud_done: {SAVED_NOTICE}")
    versions_section(user["id"], meta)
    delete_my_app(user["id"], meta["name"])


def toast_after_rerun(message):
    """st.toast right before st.rerun() is lost: show it on the next run instead."""
    st.session_state.pending_toast = message


def local_time(iso_date):
    """A saved UTC date in the viewer's time zone, e.g. 28/10/2026 19:40."""
    try:
        zone = ZoneInfo(st.context.timezone or "UTC")
    except Exception:
        zone = timezone.utc
    return datetime.fromisoformat(iso_date).astimezone(zone).strftime("%d/%m/%Y %H:%M")


def versions_section(uid, meta):
    """Every build of the app, newest first, with a button to go back to it."""
    try:
        versions = apps.load_versions(uid)
    except Exception:
        logging.exception("Loading versions failed")
        st.error("No hemos podido cargar las versiones. Inténtalo de nuevo en un rato.")
        return
    if not versions:
        return

    with st.expander(f"Versiones ({len(versions)})", icon=":material/history:"):
        st.caption(
            f"Cada vez que se construye tu aplicación se guarda una versión "
            f"(las {apps.MAX_VERSIONS} últimas). Restaurar una no borra las demás."
        )
        for number, version in reversed(list(enumerate(versions, start=1))):
            is_current = version["id"] == meta.get("version")
            label, details, action = st.columns([3, 2, 2], vertical_alignment="center")
            label.markdown(
                f"**Versión {number}**" + (" · la que tienes ahora" if is_current else "")
                + f"  \n{local_time(version['created_at'])}"
            )
            with details.popover("Lo que pediste", icon=":material/description:"):
                show_requirements(version["requirements"])
            if not is_current and action.button(
                "Restaurar", key=f"restore_{version['id']}", icon=":material/restore:"
            ):
                try:
                    apps.restore(uid, version["id"])
                except Exception:
                    logging.exception("Restoring version failed")
                    st.error("No hemos podido restaurarla. Inténtalo de nuevo en un rato.")
                    return
                # The chat must start from the restored requirements.
                for key in ("saved_requirements", "chat", "pending_requirements"):
                    st.session_state.pop(key, None)
                toast_after_rerun(f"Has vuelto a la versión {number}.")
                st.rerun()


def ai_badge(app):
    """Mark apps that use AI, so their users know (and know the daily limit)."""
    if app.get("uses_ai"):
        st.badge(
            "Con IA",
            icon=":material/auto_awesome:",
            color="violet",
            help=f"Esta aplicación usa inteligencia artificial, hasta {app_ai.DAILY_LIMIT} veces al día.",
        )


def share_url(uid, meta):
    """Full address of an app's page, to copy and send, e.g. https://…/redacpro.

    Built from the domain only: on Streamlit Cloud the page runs inside an
    iframe whose own path (/~/+/) should not end up in the link. An app whose
    address could not be saved keeps the old link.
    """
    address = urlsplit(st.context.url)
    path = meta["slug"] if meta.get("slug") else f"{VIEW_URL_PATH}?app={uid}"
    return f"{address.scheme}://{address.netloc}/{path}"


def requested_slug():
    """The last part of the address the browser opened, e.g. "redacpro"."""
    return urlsplit(st.context.url).path.rstrip("/").rsplit("/", 1)[-1]


def public_app_list():
    try:
        return apps.public_apps()
    except Exception:
        logging.exception("Listing public apps failed")
        return []


def is_public_app(uid):
    try:
        meta = apps.load_meta(uid)
    except Exception:
        logging.exception("Loading app data failed")
        return False
    return bool(meta and meta.get("public"))


def public_toggle(uid, meta):
    """The "Pública" switch of an app, for its owner and for the admin."""
    key = f"public_{uid}"

    def save():
        try:
            apps.set_public(uid, st.session_state[key])
        except Exception:
            logging.exception("Changing visibility failed")
            # Back to what is saved, so the switch does not lie.
            st.session_state[key] = meta["public"]
            st.session_state.public_failed = True

    st.toggle(
        "Pública",
        value=meta["public"],
        key=key,
        on_change=save,
        help="Aparece en «Apps públicas» y la puede usar cualquiera, también sin cuenta.",
    )
    if st.session_state.pop("public_failed", False):
        st.error("No hemos podido cambiarlo. Inténtalo de nuevo en un rato.")


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
        toast_after_rerun(f"{name} borrada.")
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
            ai_badge(app)
            if app["description"]:
                st.write(app["description"])
            if app["id"] in public_app_pages:
                st.page_link(public_app_pages[app["id"]], label="Abrir", icon=":material/arrow_forward:")
            else:
                st.page_link(view_page, label="Abrir", icon=":material/arrow_forward:", query_params={"app": app["id"]})


def public_app_page(uid):
    """The page at a public app's own address, e.g. /redacpro."""

    def page():
        meta = app_meta(uid)
        if not (meta and meta.get("public")):
            # Hidden since the menu was built.
            st.title("Aplicación no disponible")
            st.write("Esta aplicación no existe o no es pública.")
            st.page_link(public_list_page, label="Ver las apps públicas", icon=":material/explore:")
            return
        st.title(meta["name"])
        ai_badge(meta)
        show_app(uid, meta)

    return page


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
        st.page_link(public_list_page, label="Ver las apps públicas", icon=":material/explore:")
        return
    if uid in public_app_pages:
        # Old links (?app=<id>) of a public app go to its own address.
        st.switch_page(public_app_pages[uid])
    meta = apps.load_meta(uid)
    st.title(meta["name"])
    ai_badge(meta)
    show_app(uid, meta)


def show_app(uid, meta=None):
    """Show the user's app in a frame. Returns False if there is none.

    Under an app that uses AI, the uses it has left today (after this run's calls).
    """
    try:
        if apps.load(uid) is None:
            return False
    except Exception:
        logging.exception("Loading app failed")
        st.error("No hemos podido cargar la aplicación. Inténtalo de nuevo en un rato.")
        return True
    with st.container(border=True):
        apps.show(uid)
    if meta and meta.get("uses_ai"):
        st.caption(
            f":material/auto_awesome: A esta aplicación le quedan {app_ai.remaining_today(uid)} "
            f"de {app_ai.DAILY_LIMIT} usos de IA hoy, entre todas las personas que la usan."
        )
    return True


def saved_requirements(uid, state=None):
    # Read once per session: in production each read is a GitHub API call.
    state = st.session_state if state is None else state
    if "saved_requirements" not in state:
        state["saved_requirements"] = storage.read_file(apps.requirements_path(uid))
    return state["saved_requirements"]


def requirements_markdown(requirements):
    """Requirements as Markdown: labels in bold, and lines after a list kept out of it."""
    lines, in_list = [], False
    for line in requirements.splitlines():
        is_item = line.lstrip().startswith("- ")
        if in_list and not is_item:
            lines.append("")
        label = REQUIREMENT_LABEL.match(line)
        if label and not is_item:
            line = f"**{label.group(1)}:**{line[label.end():]}"
        lines.append(line if is_item else f"{line}  ")
        in_list = is_item
    return "\n".join(lines)


def show_requirements(requirements):
    with st.container(border=True):
        st.markdown(requirements_markdown(requirements))


def builds_left(user):
    """Builds the user has left today (None for the admin, who has no limit)."""
    if user["role"] == auth.ROLE_ADMIN:
        return None
    return max(BUILDS_PER_DAY - usage.builds(user["id"]), 0)


def build_limit_reached(user):
    """Count a build attempt; True if the user has none left today."""
    if builds_left(user) == 0:
        return True
    usage.count_build(user["id"])
    return False


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
    finally:
        # The calls of the build, saved now rather than in a few minutes.
        usage.save_now()
    return "ok"


def analyst_page():
    user = st.session_state.user
    meta = app_meta(user["id"])
    st.title(f"Cambiar {meta['name']}" if meta else "Crea tu aplicación")
    analyst_chat(user["id"], meta, st.session_state)


def analyst_chat(uid, meta, state, owner_name=None):
    """The chat with the analyst that creates or changes the app of `uid`.

    state: where the chat lives; st.session_state for the user's own app.
    owner_name: set when the admin changes another user's app; that chat
    keeps its own state, so it does not mix with the admin's own app.
    """
    user = st.session_state.user
    saved = saved_requirements(uid, state)
    if saved:
        with st.expander("Lo que ya me pediste" if owner_name is None else f"Lo que pidió {owner_name}"):
            show_requirements(saved)
    # Changes start from the app the user already has.
    current_app = {"name": meta["name"], "requirements": saved} if meta and saved else None

    state.setdefault("chat", [])
    greeting = (
        analyst.greeting(meta and meta["name"]) if owner_name is None
        else f"¡Hola! Vas a cambiar {meta['name']}, la aplicación de {owner_name}. "
        "Cuéntame qué quieres cambiar o añadir."
    )
    st.chat_message("assistant").write(greeting)
    for message in state["chat"]:
        st.chat_message(message["role"]).write(message["content"])

    example = None
    if not meta and not state["chat"]:
        st.caption("¿No sabes por dónde empezar? Pulsa una idea o escribe la tuya:")
        columns = st.columns(2)
        for number, (label, idea) in enumerate(EXAMPLE_IDEAS):
            if columns[number % 2].button(label, key=f"idea_{number}", width="stretch"):
                example = idea

    pending = state.get("pending_requirements")
    if pending:
        show_requirements(pending)
        st.write("¿Empezamos a construirla?")
        left = builds_left(user)
        st.caption(
            "Construirla tarda 1 o 2 minutos."
            + ("" if left is None else f" Hoy puedes construirla {left} {'vez' if left == 1 else 'veces'} más.")
        )
        yes, change = st.columns(2)
        if yes.button("¡Sí, adelante!", type="primary", width="stretch"):
            if build_limit_reached(user):
                state["build_result"] = "limit"
                st.rerun()
            state["build_result"] = build_app(uid, pending)
            if state["build_result"] == "ok":
                state["saved_requirements"] = pending
                state["chat"] = []
                del state["pending_requirements"]
            st.rerun()
        if change.button("Quiero cambiar algo", width="stretch"):
            del state["pending_requirements"]
            state["chat"].append({"role": "assistant", "content": "Claro, dime qué quieres cambiar."})
            st.rerun()

    build_result = state.pop("build_result", None)
    if build_result == "ok" and owner_name is None:
        st.success(f"¡Tu aplicación {apps.load_meta(uid)['name']} está lista!")
        st.page_link(home, label="Ver mi aplicación", icon=":material/arrow_forward:")
    elif build_result == "ok":
        st.success(
            f"¡{apps.load_meta(uid)['name']} está lista! {owner_name} ya la tiene con el cambio, "
            "como una versión nueva."
        )
    elif build_result:
        st.error(BUILD_MESSAGES[build_result])

    if state.pop("ai_failed", False):
        st.error(ASTROS_MESSAGE)

    st.caption(f":material/info: {AI_DISCLAIMER}")
    prompt = st.chat_input("Escribe aquí…") or example
    if prompt:
        state.pop("pending_requirements", None)
        state["chat"].append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        try:
            text, requirements = waiting.run(analyst.reply, state["chat"], current_app)
        except llm.AIUnavailable:
            # Rerun so the unanswered message also disappears from the screen.
            state["chat"].pop()
            state["ai_failed"] = True
            st.rerun()
        state["chat"].append({"role": "assistant", "content": text})
        if requirements:
            state["pending_requirements"] = requirements
        st.rerun()


def delete_my_account(user):
    """A registered user deletes their account, app and versions, and is logged out."""
    with st.popover("Borrar mi cuenta", icon=":material/person_remove:"):
        st.warning(
            "Se borrarán tu cuenta, tu aplicación y todas sus versiones. "
            "No se puede deshacer."
        )
        if st.button("Sí, borrar mi cuenta", type="primary", key="delete_my_account"):
            try:
                auth.delete_user(user["id"])
                apps.clear_caches()
            except Exception:
                logging.exception("Deleting own account failed")
                st.error("No hemos podido borrar tu cuenta. Inténtalo de nuevo en un rato.")
                return
            st.session_state.clear()
            # Like "Salir": the session cookie is cleared and the old one ignored.
            st.session_state.logged_out = True
            toast_after_rerun("Tu cuenta se ha borrado.")
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


def users_list():
    """Every registered user in a row; the name opens their page."""
    users = registered_users()
    if not users:
        st.write("Todavía no hay nadie registrado.")
        return
    st.caption(f"{len(users)} usuarios. Pulsa un nombre para ver su aplicación.")
    widths = [3, 2, 2, 3]
    for column, title in zip(st.columns(widths), ["Usuario", "Registrado", "Último acceso", "Aplicación"]):
        column.markdown(f"**{title}**")
    for registered in users:
        try:
            meta = apps.load_meta(registered["id"])
        except Exception:
            logging.exception("Loading app data failed")
            meta = None
        name, created, last, app = st.columns(widths, vertical_alignment="center")
        if name.button(registered["name"], key=f"user_{registered['id']}", icon=":material/person:"):
            st.session_state.selected_user = registered["id"]
            st.session_state.pop("confirm_delete", None)
            st.rerun()
        created.write(local_time(registered["created_at"]) if registered["created_at"] else "—")
        last.write(local_time(registered["last_access"]) if registered["last_access"] else "—")
        app.write(
            (meta["name"] + (" · pública" if meta["public"] else "") + (" · con IA" if meta.get("uses_ai") else ""))
            if meta else "No tiene"
        )


def users_page():
    st.title("Usuarios")
    user = selected_user()
    if user is None:
        users_list()
        return

    if st.session_state.get("editing_user") == user["id"]:
        change_user_app(user)
        return

    if st.button("Todos los usuarios", icon=":material/arrow_back:", type="tertiary"):
        del st.session_state.selected_user
        st.session_state.pop("confirm_delete", None)
        st.rerun()
    st.header(user["name"])
    st.caption(
        f"Registrado el {local_time(user['created_at']) if user['created_at'] else '—'} · "
        f"último acceso el {local_time(user['last_access']) if user['last_access'] else '—'}"
    )

    meta = app_meta(user["id"])
    st.subheader(f"Su aplicación: {meta['name']}" if meta else "Su aplicación")
    if meta:
        ai_badge(meta)
    if meta:
        public_toggle(user["id"], meta)
        if st.button("Cambiar su aplicación", icon=":material/edit:"):
            st.session_state.editing_user = user["id"]
            st.rerun()
    if not show_app(user["id"], meta):
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
        toast_after_rerun(f"{user['name']} borrado.")
        st.rerun()
    if cancel.button("Cancelar", width="stretch"):
        del st.session_state.confirm_delete
        st.rerun()


def change_user_app(user):
    """Only the admin: the analyst's chat on another user's app, from "Usuarios".

    The build is saved in the user's folder as a new version, as if they had
    asked for it; the name and the visibility do not change.
    """
    if st.session_state.user["role"] != auth.ROLE_ADMIN:
        st.stop()
    if st.button(f"Volver a {user['name']}", icon=":material/arrow_back:", type="tertiary"):
        del st.session_state.editing_user
        st.rerun()
    meta = app_meta(user["id"])
    if meta is None:
        del st.session_state.editing_user
        st.rerun()
    st.header(f"Cambiar {meta['name']}, de {user['name']}")
    analyst_chat(
        user["id"], meta, st.session_state.setdefault(f"edit_{user['id']}", {}), owner_name=user["name"]
    )


def _sum_roles(models):
    """Calls per role, from {model: {role: calls}}."""
    return {role: sum(calls.get(role, 0) for calls in models.values()) for role in usage.ROLES}


@st.cache_data(ttl=600, show_spinner=False)
def past_day_usage(day):
    return usage.day_usage(day)


def usage_page():
    """The admin sees how much AI is used: today, per model, app and user, and the last days."""
    st.title("Consumo de la IA")
    st.caption(
        f"Hoy es {usage.today()} (los días cuentan en hora UTC). Cuánta cuota queda en Google "
        "no lo dice su API: se ve en Google AI Studio."
    )
    st.link_button("Ver la cuota en Google AI Studio", AI_STUDIO_USAGE_URL, icon=":material/open_in_new:")

    today = usage.day_usage()
    roles = _sum_roles(today["models"])
    total, analyst_calls, developer_calls, apps_calls = st.columns(4)
    total.metric("Llamadas hoy", sum(roles.values()))
    analyst_calls.metric("Del analista", roles["analista"])
    developer_calls.metric("Del desarrollador", roles["desarrollador"])
    apps_calls.metric("De las apps", roles["apps"])

    st.subheader("Modelos")
    try:
        models = llm.available_models()
    except Exception:
        logging.exception("Listing models failed")
        st.warning("No hemos podido listar los modelos de Google. Se ven solo los que se han usado hoy.")
        models = []
    seen = set(today["models"]) | set(today["failures"]) | set(today["resting"])
    rows = []
    for model in models + sorted(seen - set(models)):
        rest = today["resting"].get(model)
        resting = rest and rest["until"] > time.time()
        calls = today["models"].get(model, {})
        rows.append({
            "Modelo": model,
            "Estado": f"Apartado hasta {local_time(datetime.fromtimestamp(rest['until'], timezone.utc).isoformat())} ({rest['reason']})"
            if resting else "Disponible",
            **{role.capitalize(): calls.get(role, 0) for role in usage.ROLES},
            "Fallos hoy": ", ".join(
                f"{reason}: {count}" for reason, count in today["failures"].get(model, {}).items()
            ),
        })
    st.caption("En orden de preferencia para el analista y el desarrollador; las apps empiezan por los más ligeros.")
    st.dataframe(rows, hide_index=True)

    names = {registered["id"]: registered["name"] for registered in registered_users()}
    st.subheader("Apps con IA")
    if not today["apps"]:
        st.caption("Hoy ninguna app ha usado la IA.")
    else:
        app_rows = []
        for uid, count in sorted(today["apps"].items(), key=lambda item: -item[1]):
            meta = app_meta(uid)
            app_rows.append({
                "App": meta["name"] if meta else "(borrada)",
                "Dueño": names.get(uid, uid),
                "Usos hoy": f"{count} de {app_ai.DAILY_LIMIT}",
            })
        st.dataframe(app_rows, hide_index=True)

    st.subheader("Construcciones")
    if not today["builds"]:
        st.caption("Hoy nadie ha construido su aplicación (el admin no cuenta).")
    else:
        st.dataframe(
            [
                {"Usuario": names.get(uid, uid), "Construcciones hoy": f"{count} de {BUILDS_PER_DAY}"}
                for uid, count in sorted(today["builds"].items(), key=lambda item: -item[1])
            ],
            hide_index=True,
        )

    st.subheader("Días anteriores")
    try:
        days = [day for day in usage.saved_days() if day != usage.today()][:PAST_DAYS]
        history = [(day, past_day_usage(day)) for day in days]
    except Exception:
        logging.exception("Reading usage history failed")
        st.error("No hemos podido leer los días anteriores. Inténtalo de nuevo en un rato.")
        return
    if not history:
        st.caption("Todavía no hay días anteriores guardados.")
        return
    st.dataframe(
        [
            {
                "Día": day,
                **{role.capitalize(): count for role, count in _sum_roles(data["models"]).items()},
                "Fallos": sum(sum(reasons.values()) for reasons in data["failures"].values()),
                "Construcciones": sum(data["builds"].values()),
            }
            for day, data in history
        ],
        hide_index=True,
    )


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
if not logged_out and (user is None or st.session_state.get("shared_guest")):
    restored = restored_user(browser_token)
    if restored:
        user = st.session_state.user = restored
    # A saved session wins over the guest of a shared link, but only until the
    # browser has answered (on Streamlit Cloud it answers one rerun later).
    if restored or browser_token is not None:
        st.session_state.shared_guest = False
shared_app = st.query_params.get("app")
public_apps = public_app_list()
opens_public_app = (shared_app and is_public_app(shared_app)) or (
    user is None and requested_slug() in {app["slug"] for app in public_apps if app["slug"]}
)
if user is None and not logged_out and opens_public_app:
    # A link to a public app opens without logging in; this guest is not remembered.
    user = st.session_state.user = auth.guest()
    st.session_state.shared_guest = browser_token is None
# Before the login page too: e.g. "Tu cuenta se ha borrado." after deleting the account.
if message := st.session_state.pop("pending_toast", None):
    st.toast(message)
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
# Each public app at its own address (e.g. /redacpro), for everyone, not in the menu.
public_app_pages = {
    app["id"]: st.Page(
        public_app_page(app["id"]), title=app["name"], url_path=app["slug"], visibility="hidden"
    )
    for app in public_apps
    if app["slug"]
}
admin_users_page = st.Page(users_page, title="Usuarios", url_path=USERS_URL_PATH)
admin_usage_page = st.Page(usage_page, title="Consumo", url_path=USAGE_URL_PATH)
if is_guest:
    pages = [public_list_page, view_page]
elif my_app:
    pages = [home, my_app_page, public_list_page, view_page]
else:
    pages = [my_app_page, public_list_page, view_page]
if user["role"] == auth.ROLE_ADMIN:
    pages += [admin_users_page, admin_usage_page]
pages += list(public_app_pages.values())
# Reached from links, not from the menu: the apps' pages, and the chat to change
# your app (its link is on the app's page).
off_menu = [view_page, *public_app_pages.values()] + ([my_app_page] if my_app else [])
# Our own menu, so the logo can go above it at a readable size
# (st.logo is at most 32px high).
navigation = st.navigation(pages, position="hidden")
# Coming to "Usuarios" from another page shows the list, not the last user opened.
if navigation.url_path == USERS_URL_PATH and st.session_state.get("current_page") != USERS_URL_PATH:
    st.session_state.pop("selected_user", None)
    st.session_state.pop("editing_user", None)
st.session_state.current_page = navigation.url_path
if shared_app and navigation.url_path != VIEW_URL_PATH:
    # Logging in from a shared link loses the page ("/app" becomes "/"): go back to it.
    st.switch_page(view_page, query_params={"app": shared_app})

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
    if user["role"] == auth.ROLE_USER:
        delete_my_account(user)

navigation.run()
