"""The users' apps, run behind the guardrails.

Each user has at most one app, in users/<user_id>/:
- app.py: its code.
- app.json: {"name", "public", "description", "version", "uses_ai", "slug"}. Private by default.
  "slug" is the app's address once it has been public (e.g. /redacpro): it is
  given the first time and never changes, so shared links keep working.
- requisitos.md: the requirements it was built from.
- versiones/<id>.json: every build, {"created_at", "code", "requirements"},
  so the owner can go back to an older one. Only the last MAX_VERSIONS stay.
"""

import ast
import json
import logging
import re
import unicodedata
from datetime import datetime, timezone

import streamlit as st

import app_ai
import auth
import guardrails
import storage

DESCRIPTION_PATTERN = re.compile(r"^Para qué sirve:\s*(.+)$", re.MULTILINE)
MAX_VERSIONS = 10
# Addresses an app cannot take: Yahoraque's pages (see the *_URL_PATH in app.py)
# and the paths Streamlit's server uses.
RESERVED_SLUGS = {
    "mi-app", "usuarios", "publicas", "app", "consumo",
    "static", "media", "component", "healthz", "stcore", "vendor",
}  # fmt: skip


def app_path(uid):
    return f"{auth.USERS_DIR}/{uid}/app.py"


def meta_path(uid):
    return f"{auth.USERS_DIR}/{uid}/app.json"


def requirements_path(uid):
    return f"{auth.USERS_DIR}/{uid}/requisitos.md"


def code_uses_ai(code):
    """Whether the app calls ia(): it is marked "Con IA" for its users."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False
    return any(
        isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "ia"
        for node in ast.walk(tree)
    )


def versions_dir(uid):
    return f"{auth.USERS_DIR}/{uid}/versiones"


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


@st.cache_data(ttl=600, show_spinner=False)
def load_versions(uid):
    """The app's versions, oldest first: [{"id", "created_at", "code", "requirements"}].

    Cached because on GitHub each version is one API call.
    """
    versions = []
    for file_name in storage.list_dir(versions_dir(uid)):
        data = storage.read_file(f"{versions_dir(uid)}/{file_name}")
        if data:
            versions.append({"id": file_name.removesuffix(".json"), **json.loads(data)})
    return sorted(versions, key=lambda version: version["id"])


def clear_caches():
    """Forget cached apps, e.g. after one changes or its user is deleted."""
    load.clear()
    load_meta.clear()
    load_versions.clear()
    public_apps.clear()


def _save_version(uid, code, requirements):
    now = datetime.now(timezone.utc)
    # Sortable and unique even for two saves in the same second.
    version_id = now.strftime("%Y%m%dT%H%M%S%fZ")
    data = {"created_at": now.isoformat(), "code": code, "requirements": requirements}
    storage.write_file(
        f"{versions_dir(uid)}/{version_id}.json", json.dumps(data, indent=2), f"App {uid}: versión"
    )
    return version_id


def save(uid, code, requirements, name, public):
    """Save a new build as the current app and as a new version."""
    versions = load_versions(uid)
    previous = load(uid)
    if not versions and previous is not None:
        # An app from before versions existed: keep it as the first one.
        _save_version(uid, previous, storage.read_file(requirements_path(uid)) or "")
    version_id = _save_version(uid, code, requirements)

    description = DESCRIPTION_PATTERN.search(requirements)
    meta = {
        "name": name,
        "public": public,
        "description": description.group(1).strip() if description else "",
        "version": version_id,
        "uses_ai": code_uses_ai(code),
    }
    slug = (load_meta(uid) or {}).get("slug")
    if slug:
        meta["slug"] = slug
    storage.write_file(app_path(uid), code, f"App {uid}")
    storage.write_file(meta_path(uid), json.dumps(meta, indent=2), f"App {uid}: datos")
    storage.write_file(requirements_path(uid), requirements, f"Requisitos {uid}")

    kept = sorted(storage.list_dir(versions_dir(uid)))
    for old in kept[:-MAX_VERSIONS]:
        storage.delete_file(f"{versions_dir(uid)}/{old}", f"App {uid}: versión antigua")
    clear_caches()


def restore(uid, version_id):
    """Make an older version the current app. No version is lost."""
    version = next(version for version in load_versions(uid) if version["id"] == version_id)
    meta = {**load_meta(uid), "version": version_id, "uses_ai": code_uses_ai(version["code"])}
    description = DESCRIPTION_PATTERN.search(version["requirements"])
    if description:
        meta["description"] = description.group(1).strip()
    storage.write_file(app_path(uid), version["code"], f"App {uid}: restaurar versión")
    storage.write_file(meta_path(uid), json.dumps(meta, indent=2), f"App {uid}: datos")
    storage.write_file(requirements_path(uid), version["requirements"], f"Requisitos {uid}")
    clear_caches()


def set_public(uid, public):
    meta = {**load_meta(uid), "public": public}
    if public and not meta.get("slug"):
        meta["slug"] = slug_for(meta["name"], taken_slugs())
    storage.write_file(meta_path(uid), json.dumps(meta, indent=2), f"App {uid}: pública={public}")
    clear_caches()


def slug_for(name, taken):
    """The app's address from its name: «Redacpro» -> "redacpro".

    In lowercase, without accents. If another app or a Yahoraque page already
    has it, the first free of "redacpro-2", "redacpro-3"…
    """
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    base = re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-") or "app"
    slug, number = base, 1
    while slug in taken or slug in RESERVED_SLUGS:
        number += 1
        slug = f"{base}-{number}"
    return slug


def taken_slugs():
    """Addresses already given to some app, public or not."""
    taken = set()
    for user in auth.list_users():
        meta = load_meta(user["id"])
        if meta and meta.get("slug"):
            taken.add(meta["slug"])
    return taken


def delete(uid):
    """Delete the app, its requirements and its versions; the account stays."""
    for path in (app_path(uid), meta_path(uid), requirements_path(uid)):
        storage.delete_file(path, f"Borrar app {uid}")
    storage.delete_dir(versions_dir(uid), f"Borrar versiones {uid}")
    clear_caches()


@st.cache_data(ttl=300, show_spinner=False)
def public_apps():
    """Public apps sorted by name: [{"id", "name", "description", "uses_ai", "slug"}].

    Cached because on GitHub each user's app.json is one API call. Public apps
    from before addresses existed get theirs here, once.
    """
    metas = {user["id"]: load_meta(user["id"]) for user in auth.list_users()}
    taken = {meta["slug"] for meta in metas.values() if meta and meta.get("slug")}
    found = []
    for uid, meta in sorted(metas.items(), key=lambda item: item[1]["name"].lower() if item[1] else ""):
        if not (meta and meta.get("public")):
            continue
        if not meta.get("slug"):
            meta = _give_slug(uid, meta, taken)
        found.append(
            {
                "id": uid,
                "name": meta["name"],
                "description": meta.get("description", ""),
                "uses_ai": meta.get("uses_ai", False),
                "slug": meta.get("slug"),
            }
        )
    return found


def _give_slug(uid, meta, taken):
    """Save an address for an app that has none. If it cannot, the app keeps its old link."""
    slug = slug_for(meta["name"], taken)
    try:
        storage.write_file(
            meta_path(uid), json.dumps({**meta, "slug": slug}, indent=2), f"App {uid}: dirección {slug}"
        )
    except Exception:
        logging.exception("Saving the address of app %s failed", uid)
        return meta
    taken.add(slug)
    load_meta.clear()
    return {**meta, "slug": slug}


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
    except app_ai.IAError as error:
        # Daily limit, AI unavailable…: the message is meant for the viewer.
        st.warning(str(error), icon=":material/auto_awesome:")
    except Exception:
        # Stopping or rerunning the page are not Exceptions, so they pass through.
        logging.exception("App %s failed", uid)
        st.error("La aplicación ha tenido un problema. Prueba a recargar la página.")
    return True
