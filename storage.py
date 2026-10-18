"""File storage: local disk for development, GitHub for production.

The STORAGE_MODE secret selects the backend: "local" (default) or "github".
"""

import base64
import os
from pathlib import Path

import requests
import streamlit as st

BRANCH = "master"
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


def push_file(path, content, message):
    """Create or update a file on GitHub. Returns the new commit SHA.

    Retries when another save changed the file at the same time.
    """
    url, headers = _github_request(path)
    for attempt in range(PUSH_ATTEMPTS):
        current = requests.get(url, headers=headers, params={"ref": BRANCH}, timeout=30)
        body = {
            "message": message,
            "content": base64.b64encode(content.encode()).decode(),
            "branch": BRANCH,
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
        response = requests.get(url, headers=headers, params={"ref": BRANCH}, timeout=30)
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
