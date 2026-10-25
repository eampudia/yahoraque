"""The users' apps: stored in users/<user_id>/app.py and run behind the guardrails."""

import logging

import streamlit as st

import auth
import guardrails
import storage


def app_path(uid):
    return f"{auth.USERS_DIR}/{uid}/app.py"


@st.cache_data(ttl=600, show_spinner=False)
def load(uid):
    """The app's code, or None if the user has no app yet.

    Cached because on GitHub each read is an API call, and an app reruns on every click.
    """
    return storage.read_file(app_path(uid))


def save(uid, code):
    storage.write_file(app_path(uid), code, f"App {uid}")
    load.clear()


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
