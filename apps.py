"""The users' apps, run behind the guardrails.

Each user has at most one app, in users/<user_id>/:
- app.py: its code.
- app.json: {"name", "public", "description"}. Private by default.
- requisitos.md: the requirements it was built from.
"""

import json
import logging
import re

import streamlit as st

import auth
import guardrails
import storage

DESCRIPTION_PATTERN = re.compile(r"^Para qué sirve:\s*(.+)$", re.MULTILINE)


def app_path(uid):
    return f"{auth.USERS_DIR}/{uid}/app.py"


def meta_path(uid):
    return f"{auth.USERS_DIR}/{uid}/app.json"


def requirements_path(uid):
    return f"{auth.USERS_DIR}/{uid}/requisitos.md"


@st.cache_data(ttl=600, show_spinner=False)
def load(uid):
    """The app's code, or None if the user has no app yet.

    Cached because on GitHub each read is an API call, and an app reruns on every click.
    """
    return storage.read_file(app_path(uid))


@st.cache_data(ttl=600, show_spinner=False)
def load_meta(uid):
    """The app's name, visibility and description, or None if there is no app."""
    data = storage.read_file(meta_path(uid))
    return json.loads(data) if data else None


def clear_caches():
    """Forget cached apps, e.g. after one changes or its user is deleted."""
    load.clear()
    load_meta.clear()
    public_apps.clear()


def save(uid, code, requirements, name, public):
    description = DESCRIPTION_PATTERN.search(requirements)
    meta = {
        "name": name,
        "public": public,
        "description": description.group(1).strip() if description else "",
    }
    storage.write_file(app_path(uid), code, f"App {uid}")
    storage.write_file(meta_path(uid), json.dumps(meta, indent=2), f"App {uid}: datos")
    storage.write_file(requirements_path(uid), requirements, f"Requisitos {uid}")
    clear_caches()


def set_public(uid, public):
    meta = {**load_meta(uid), "public": public}
    storage.write_file(meta_path(uid), json.dumps(meta, indent=2), f"App {uid}: pública={public}")
    clear_caches()


def delete(uid):
    """Delete the app and its requirements; the account stays."""
    for path in (app_path(uid), meta_path(uid), requirements_path(uid)):
        storage.delete_file(path, f"Borrar app {uid}")
    clear_caches()


@st.cache_data(ttl=300, show_spinner=False)
def public_apps():
    """Public apps sorted by name: [{"id", "name", "description"}].

    Cached because on GitHub each user's app.json is one API call.
    """
    found = []
    for user in auth.list_users():
        meta = load_meta(user["id"])
        if meta and meta.get("public"):
            found.append(
                {"id": user["id"], "name": meta["name"], "description": meta.get("description", "")}
            )
    return sorted(found, key=lambda app: app["name"].lower())


def can_view(uid, viewer):
    """Public apps are for everyone; private ones only for their owner and the admin."""
    meta = load_meta(uid)
    if meta is None:
        return False
    return meta.get("public") or viewer["id"] == uid or viewer["role"] == auth.ROLE_ADMIN


def show(uid):
    """Run the user's app on the page. Returns False if there is no app."""
    code = load(uid)
    if code is None:
        return False
    try:
        guardrails.run(code, uid)
    except Exception:
        # Stopping or rerunning the page are not Exceptions, so they pass through.
        logging.exception("App %s failed", uid)
        st.error("La aplicación ha tenido un problema. Prueba a recargar la página.")
    return True
