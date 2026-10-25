"""Access with name + PIN, guest access and admin login.

Each user is stored in users/<user_id>/user.json, where user_id is a hash
of the normalized name. The file keeps the name so the admin can tell users
apart. The PIN is never stored: only an HMAC of it keyed with the
PIN_SECRET secret, so the public repo does not reveal it.

To survive a page reload, the browser keeps a signed session token (see
session_token and restore_session).
"""

import base64
import hashlib
import hmac
import json
import time
from datetime import datetime, timezone

import streamlit as st

import storage

USERS_DIR = "users"
ROLE_GUEST = "guest"
ROLE_USER = "user"
ROLE_ADMIN = "admin"
SESSION_DAYS = 7


class LoginError(Exception):
    """A login problem with a message that can be shown to the user."""


def normalize_name(name):
    return name.strip().lower()


def user_id(name):
    return hashlib.sha256(normalize_name(name).encode()).hexdigest()[:12]


def _user_path(uid):
    return f"{USERS_DIR}/{uid}/user.json"


def _hash_pin(uid, pin):
    secret = storage.get_secret("PIN_SECRET")
    if not secret:
        raise RuntimeError("Falta el secreto PIN_SECRET.")
    return hmac.new(secret.encode(), f"{uid}:{pin}".encode(), hashlib.sha256).hexdigest()


def _is_admin_name(name):
    admin_name = storage.get_secret("ADMIN_NAME")
    return bool(admin_name) and normalize_name(name) == normalize_name(admin_name)


def _session(role, name, created_at=None):
    session = {"role": role, "id": user_id(name), "name": name.strip()}
    if created_at:
        # Tells this account apart from a later one with the same name.
        session["created_at"] = created_at
    return session


def guest():
    return {"role": ROLE_GUEST, "id": None, "name": "Invitado"}


def login(name, pin):
    """Return the session for an existing user or the admin."""
    if not normalize_name(name) or not pin:
        raise LoginError("Escribe tu nombre y tu PIN.")

    if _is_admin_name(name):
        admin_password = storage.get_secret("ADMIN_PASSWORD") or ""
        if admin_password and hmac.compare_digest(pin, admin_password):
            return _session(ROLE_ADMIN, name)
        raise LoginError("Nombre o PIN incorrectos.")

    uid = user_id(name)
    data = storage.read_file(_user_path(uid))
    if data is None:
        raise LoginError("No hay nadie con ese nombre. Si eres nuevo, ve a «Soy nuevo».")
    stored = json.loads(data)
    if not hmac.compare_digest(stored["pin_hash"], _hash_pin(uid, pin)):
        raise LoginError("Nombre o PIN incorrectos.")
    return _session(ROLE_USER, name, stored.get("created_at"))


def register(name, pin):
    """Create a new user and return its session."""
    if not normalize_name(name):
        raise LoginError("Escribe un nombre.")
    if not (pin.isdigit() and 4 <= len(pin) <= 8):
        raise LoginError("El PIN tiene que tener entre 4 y 8 números.")
    if _is_admin_name(name):
        raise LoginError("Ese nombre ya está cogido. Prueba con otro.")

    uid = user_id(name)
    path = _user_path(uid)
    if storage.read_file(path) is not None:
        raise LoginError("Ese nombre ya está cogido. Prueba con otro.")

    user = {
        "name": name.strip(),
        "pin_hash": _hash_pin(uid, pin),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    storage.write_file(path, json.dumps(user, indent=2), f"Nuevo usuario {uid}")
    list_users.clear()
    return _session(ROLE_USER, name, user["created_at"])


@st.cache_data(ttl=300, show_spinner=False)
def list_users():
    """Registered users, sorted by name: [{"id", "name", "created_at"}].

    Cached because on GitHub each user is one API call.
    """
    users = []
    for uid in storage.list_dir(USERS_DIR):
        data = storage.read_file(_user_path(uid))
        user = json.loads(data) if data else {}
        users.append(
            {
                "id": uid,
                # Users created before names were stored only have their hash.
                "name": user.get("name") or uid,
                "created_at": user.get("created_at"),
            }
        )
    return sorted(users, key=lambda user: normalize_name(user["name"]))


def delete_user(uid):
    """Delete the user's folder: account, requirements and app."""
    storage.delete_dir(f"{USERS_DIR}/{uid}", f"Borrar usuario {uid}")
    list_users.clear()


def _sign(payload, role):
    secret = storage.get_secret("PIN_SECRET")
    if not secret:
        raise RuntimeError("Falta el secreto PIN_SECRET.")
    key = f"session:{secret}"
    if role == ROLE_ADMIN:
        # Changing the admin password closes the admin's open sessions.
        key += f":{storage.get_secret('ADMIN_PASSWORD') or ''}"
    return hmac.new(key.encode(), payload.encode(), hashlib.sha256).hexdigest()


def session_token(session):
    """A signed token that lets this session come back after a reload."""
    data = {**session, "expires": int(time.time()) + SESSION_DAYS * 24 * 60 * 60}
    payload = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()
    return f"{payload}.{_sign(payload, session['role'])}"


def restore_session(token):
    """Return the session stored in a token, or None if it is not valid anymore."""
    try:
        payload, signature = token.rsplit(".", 1)
        data = json.loads(base64.urlsafe_b64decode(payload))
        role = data["role"]
        expires = data.pop("expires")
    except (AttributeError, KeyError, TypeError, ValueError):
        return None
    if not hmac.compare_digest(signature, _sign(payload, role)) or expires < time.time():
        return None

    if role == ROLE_ADMIN:
        return data if _is_admin_name(data["name"]) else None
    if role == ROLE_USER:
        stored = storage.read_file(_user_path(data["id"]))
        # Deleted, or deleted and registered again by someone else.
        if stored is None or json.loads(stored).get("created_at") != data.get("created_at"):
            return None
        return data
    return data if role == ROLE_GUEST else None
