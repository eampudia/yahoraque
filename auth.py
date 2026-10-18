"""Access with name + PIN, guest access and admin login.

Each user is stored in users/<user_id>/user.json, where user_id is a hash
of the normalized name. The PIN is never stored: only an HMAC of it keyed
with the PIN_SECRET secret, so the public repo does not reveal it.
"""

import hashlib
import hmac
import json
from datetime import datetime, timezone

import storage

ROLE_GUEST = "guest"
ROLE_USER = "user"
ROLE_ADMIN = "admin"


class LoginError(Exception):
    """A login problem with a message that can be shown to the user."""


def normalize_name(name):
    return name.strip().lower()


def user_id(name):
    return hashlib.sha256(normalize_name(name).encode()).hexdigest()[:12]


def _user_path(uid):
    return f"users/{uid}/user.json"


def _hash_pin(uid, pin):
    secret = storage.get_secret("PIN_SECRET")
    if not secret:
        raise RuntimeError("Falta el secreto PIN_SECRET.")
    return hmac.new(secret.encode(), f"{uid}:{pin}".encode(), hashlib.sha256).hexdigest()


def _is_admin_name(name):
    admin_name = storage.get_secret("ADMIN_NAME")
    return bool(admin_name) and normalize_name(name) == normalize_name(admin_name)


def _session(role, name):
    return {"role": role, "id": user_id(name), "name": name.strip()}


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
    if not hmac.compare_digest(json.loads(data)["pin_hash"], _hash_pin(uid, pin)):
        raise LoginError("Nombre o PIN incorrectos.")
    return _session(ROLE_USER, name)


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
        "pin_hash": _hash_pin(uid, pin),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    storage.write_file(path, json.dumps(user, indent=2), f"Nuevo usuario {uid}")
    return _session(ROLE_USER, name)
