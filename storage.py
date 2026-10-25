"""File storage: local disk for development, GitHub for production.

The STORAGE_MODE secret selects the backend: "local" (default) or "github".
On GitHub, user data lives in its own branch (DATA_BRANCH, default "datos"),
never in the code branch that Streamlit deploys.
"""

import base64
import os
import shutil
from pathlib import Path

import requests
import streamlit as st

DEFAULT_DATA_BRANCH = "datos"
LOCAL_DIR = Path(__file__).parent / ".data"
PUSH_ATTEMPTS = 3


def get_secret(name):
    """Read a secret from the environment (local) or Streamlit secrets (cloud)."""
    value = os.environ.get(name)
    if value:
        return value
    try:
        return st.secrets[name]
    except Exception:
        return None


def _data_branch():
    return get_secret("DATA_BRANCH") or DEFAULT_DATA_BRANCH


def _use_github():
    return (get_secret("STORAGE_MODE") or "local").lower() == "github"


def _github_request(path):
    repo = get_secret("GITHUB_REPO")
    token = get_secret("GITHUB_TOKEN")
    if not repo or not token:
        raise RuntimeError("Faltan los secretos GITHUB_REPO o GITHUB_TOKEN.")
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    return url, headers


@st.cache_resource
def _ensure_data_branch():
    """Create the data branch from the default branch if it does not exist yet."""
    repo_url = f"https://api.github.com/repos/{get_secret('GITHUB_REPO')}"
    _, headers = _github_request("")
    branch = _data_branch()
    response = requests.get(f"{repo_url}/branches/{branch}", headers=headers, timeout=30)
    if response.status_code == 200:
        return
    if response.status_code != 404:
        response.raise_for_status()

    default = requests.get(repo_url, headers=headers, timeout=30)
    default.raise_for_status()
    base = requests.get(
        f"{repo_url}/branches/{default.json()['default_branch']}", headers=headers, timeout=30
    )
    base.raise_for_status()
    created = requests.post(
        f"{repo_url}/git/refs",
        headers=headers,
        json={"ref": f"refs/heads/{branch}", "sha": base.json()["commit"]["sha"]},
        timeout=30,
    )
    # 422: another session created it at the same time.
    if created.status_code != 422:
        created.raise_for_status()


def push_file(path, content, message):
    """Create or update a file on GitHub. Returns the new commit SHA.

    Retries when another save changed the file at the same time.
    """
    _ensure_data_branch()
    url, headers = _github_request(path)
    for attempt in range(PUSH_ATTEMPTS):
        current = requests.get(url, headers=headers, params={"ref": _data_branch()}, timeout=30)
        body = {
            "message": message,
            "content": base64.b64encode(content.encode()).decode(),
            "branch": _data_branch(),
        }
        if current.status_code == 200:
            body["sha"] = current.json()["sha"]

        response = requests.put(url, headers=headers, json=body, timeout=30)
        if response.status_code == 409 and attempt < PUSH_ATTEMPTS - 1:
            continue
        response.raise_for_status()
        return response.json()["commit"]["sha"]


def read_file(path):
    """Return the file content, or None if it does not exist."""
    if _use_github():
        url, headers = _github_request(path)
        response = requests.get(url, headers=headers, params={"ref": _data_branch()}, timeout=30)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return base64.b64decode(response.json()["content"]).decode()

    file = LOCAL_DIR / path
    return file.read_text() if file.exists() else None


def write_file(path, content, message):
    if _use_github():
        push_file(path, content, message)
        return

    file = LOCAL_DIR / path
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(content)


def list_dir(path):
    """Return the names of the entries in a folder, or [] if it does not exist."""
    if _use_github():
        url, headers = _github_request(path)
        response = requests.get(url, headers=headers, params={"ref": _data_branch()}, timeout=30)
        if response.status_code == 404:
            return []
        response.raise_for_status()
        return sorted(entry["name"] for entry in response.json())

    folder = LOCAL_DIR / path
    return sorted(entry.name for entry in folder.iterdir()) if folder.is_dir() else []


def _delete_github_dir(path, message):
    url, headers = _github_request(path)
    response = requests.get(url, headers=headers, params={"ref": _data_branch()}, timeout=30)
    if response.status_code == 404:
        return
    response.raise_for_status()
    for entry in response.json():
        if entry["type"] == "dir":
            _delete_github_dir(entry["path"], message)
            continue
        file_url, _ = _github_request(entry["path"])
        deleted = requests.delete(
            file_url,
            headers=headers,
            json={"message": message, "sha": entry["sha"], "branch": _data_branch()},
            timeout=30,
        )
        deleted.raise_for_status()


def delete_dir(path, message):
    """Delete a folder and everything in it. Git history keeps the old versions."""
    if _use_github():
        _delete_github_dir(path, message)
        return

    shutil.rmtree(LOCAL_DIR / path, ignore_errors=True)
