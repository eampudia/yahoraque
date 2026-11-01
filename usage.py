"""How much AI Yahoraque uses each day, saved in the data branch.

One file per UTC day (uso/<date>.json) with the calls per model and role,
the failures, the models resting, the AI uses of each app and the builds of
each user. The daily limits read it, so they survive a server restart.

Counting must not make every AI call slower, so only what was added since the
last save is kept in memory (`pending`) and added to the file at most every
SAVE_EVERY seconds (builds, right away). The file is read again before each
save, so a failed read never overwrites counts with smaller ones.
"""

import copy
import json
import logging
import threading
import time
from datetime import datetime, timezone

import streamlit as st

import storage

USAGE_DIR = "uso"
SAVE_EVERY = 5 * 60
# Who asked the AI.
ROLES = ("analista", "desarrollador", "apps")


def today():
    return datetime.now(timezone.utc).date().isoformat()


def _path(day):
    return f"{USAGE_DIR}/{day}.json"


def _empty():
    return {"models": {}, "failures": {}, "resting": {}, "apps": {}, "builds": {}}


@st.cache_resource
def _state():
    # Shared by all sessions. saved: the file as last read or written; pending: added since.
    return {
        "lock": threading.Lock(),
        "day": None,
        "saved": _empty(),
        "pending": _empty(),
        "saved_at": 0.0,
    }


def _read(day):
    text = storage.read_file(_path(day))
    return {**_empty(), **json.loads(text)} if text else _empty()


def _add(total, extra):
    """Add the counts of `extra` to `total` (nested dicts of numbers). Resting: the latest wins."""
    for section, values in extra.items():
        if section == "resting":
            for model, rest in values.items():
                if rest["until"] > total["resting"].get(model, {}).get("until", 0):
                    total["resting"][model] = rest
            continue
        for key, value in values.items():
            if isinstance(value, dict):
                inner = total[section].setdefault(key, {})
                for name, number in value.items():
                    inner[name] = inner.get(name, 0) + number
            else:
                total[section][key] = total[section].get(key, 0) + value
    return total


def _start_day(state):
    """Move to a new day: save what is left of the old one and read the new one."""
    day = today()
    if state["day"] == day:
        return
    if state["day"] is not None:
        _save(state)
    resting = {
        model: rest
        for model, rest in state["saved"]["resting"].items()
        if rest["until"] > time.time()
    }
    state["day"] = day
    state["pending"] = _empty()
    try:
        state["saved"] = _read(day)
    except Exception:
        # Counting goes on; the next save reads the file again and adds to it.
        logging.exception("Reading usage failed")
        state["saved"] = _empty()
    # A model still resting from yesterday keeps resting.
    _add(state["saved"], {"resting": resting})


def _save(state):
    """Add the pending counts to the day's file. Called with the lock held."""
    pending, day = state["pending"], state["day"]
    if not any(pending.values()):
        state["saved_at"] = time.time()
        return
    try:
        total = _add(_read(day), pending)
        storage.write_file(
            _path(day), json.dumps(total, indent=2, sort_keys=True), f"Uso de la IA del {day}"
        )
    except Exception:
        # Kept in pending, to try again in the next save.
        logging.exception("Saving usage failed")
        state["saved_at"] = time.time()
        return
    state["saved"], state["pending"], state["saved_at"] = total, _empty(), time.time()


def _record(extra, save_now=False):
    state = _state()
    with state["lock"]:
        _start_day(state)
        _add(state["pending"], extra)
        if save_now or time.time() - state["saved_at"] >= SAVE_EVERY:
            _save(state)


def day_usage(day=None):
    """The usage of a day: today's with what is not saved yet, or a past day's file."""
    if day and day != today():
        return _read(day)
    state = _state()
    with state["lock"]:
        _start_day(state)
        return _add(copy.deepcopy(state["saved"]), state["pending"])


def save_now():
    state = _state()
    with state["lock"]:
        _start_day(state)
        _save(state)


def saved_days():
    """The days with a usage file, newest first."""
    return sorted((name.removesuffix(".json") for name in storage.list_dir(USAGE_DIR)), reverse=True)


# --- What the rest of Yahoraque records and asks ---

def count_call(model, role):
    _record({"models": {model: {role: 1}}})


def count_failure(model, reason, rest_seconds):
    extra = {"failures": {model: {reason: 1}}}
    if rest_seconds:
        extra["resting"] = {model: {"until": time.time() + rest_seconds, "reason": reason}}
    _record(extra)


def resting_until(model):
    """When a model that failed can be tried again (0 if it is not resting)."""
    return day_usage()["resting"].get(model, {}).get("until", 0)


def app_calls(app_id):
    return day_usage()["apps"].get(app_id, 0)


def count_app_call(app_id):
    _record({"apps": {app_id: 1}})


def builds(user_id):
    return day_usage()["builds"].get(user_id, 0)


def count_build(user_id):
    # Right away: a build takes a minute or two anyway, and the limit must not be lost.
    _record({"builds": {user_id: 1}}, save_now=True)
