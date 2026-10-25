"""Guardrails for the apps written by the AI.

Two layers, because Python cannot fully sandbox code in the same process
(see the risks in especificacion.md):

1. check() reads the code before it runs and rejects anything that could
   reach the secrets, the files or Yahoraque itself: imports outside a
   short list, and names and attributes that allow introspection. Strings
   may contain "__" (common in JavaScript and CSS): without getattr, vars or
   .format there is no way to turn them into attribute access.
2. run() executes the code with only safe builtins and a limited `st`.
   Widget keys and st.session_state get a per-app prefix, so an app cannot
   read or change the state of Yahoraque or of other apps. Media only take
   web addresses, and custom HTML/JavaScript runs in an isolated iframe.
"""

import ast
import base64
import builtins
import importlib
from types import ModuleType, SimpleNamespace

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

ALLOWED_MODULES = {
    "calendar",
    "collections",
    "datetime",
    "decimal",
    "fractions",
    "functools",
    "itertools",
    "json",
    "math",
    "random",
    "re",
    "statistics",
    "textwrap",
}

ALLOWED_ST = {
    "area_chart", "audio", "balloons", "bar_chart", "button", "caption",
    "chat_input", "chat_message", "checkbox", "code", "color_picker", "columns",
    "container", "data_editor", "dataframe", "date_input", "dialog", "divider",
    "download_button", "empty", "error", "exception", "expander", "feedback",
    "file_uploader", "form", "form_submit_button", "fragment", "header", "html",
    "image", "info", "json", "latex", "line_chart", "link_button", "markdown",
    "metric", "multiselect", "number_input", "pills", "popover", "progress",
    "radio", "rerun", "scatter_chart", "segmented_control", "select_slider",
    "selectbox", "slider", "snow", "spinner", "status", "subheader", "success",
    "table", "tabs", "text", "text_area", "text_input", "time_input", "title",
    "toast", "toggle", "update", "video", "warning", "write",
}  # fmt: skip

SAFE_BUILTINS = {
    name: getattr(builtins, name)
    for name in [
        "abs", "all", "any", "bool", "chr", "dict", "divmod", "enumerate",
        "filter", "float", "frozenset", "int", "isinstance", "len", "list",
        "map", "max", "min", "ord", "pow", "print", "range", "repr", "reversed",
        "round", "set", "slice", "sorted", "str", "sum", "tuple", "zip",
        "ArithmeticError", "Exception", "IndexError", "KeyError", "TypeError",
        "ValueError", "ZeroDivisionError",
        # Needed to define classes.
        "__build_class__",
    ]
}  # fmt: skip

FORBIDDEN_NAMES = {
    "breakpoint", "compile", "delattr", "dir", "eval", "exec", "getattr",
    "globals", "help", "input", "locals", "memoryview", "object", "open",
    "setattr", "super", "type", "vars",
}  # fmt: skip

# str.format can read attributes of its arguments; the rest give access to
# frames, code objects and tracebacks.
FORBIDDEN_ATTRIBUTES = {"format", "format_map", "mro"}
FORBIDDEN_ATTRIBUTE_PREFIXES = ("_", "ag_", "co_", "cr_", "f_", "gi_", "tb_")
# Besides ALLOWED_ST, the limited `st` has these.
ST_EXTRAS = {"components", "session_state"}
# They accept file paths, which would serve any server file to the browser.
MEDIA_FUNCTIONS = {"audio", "image", "video"}
MEDIA_ARGUMENTS = ("image", "data", "subtitles")
WEB_PREFIXES = ("http://", "https://", "data:")
# Most apps are a whole page of HTML/JavaScript.
HTML_DEFAULT_HEIGHT = 600
# st.html with it runs JavaScript in Yahoraque's page: it could steal the session cookie.
FORBIDDEN_KEYWORDS = {"unsafe_allow_javascript"}


class GuardrailError(Exception):
    """The code does something apps are not allowed to do."""


def check(code):
    """Return a description of the first forbidden thing, or None if the code is allowed."""
    try:
        tree = ast.parse(code)
    except SyntaxError as error:
        return f"Error de sintaxis en la línea {error.lineno}: {error.msg}"

    for node in ast.walk(tree):
        line = getattr(node, "lineno", "?")
        if isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            modules = [node.module or ""] if not node.level else ["."]
        else:
            modules = []
        for module in modules:
            if module.split(".")[0] not in ALLOWED_MODULES:
                return f"Línea {line}: no se puede importar «{module}»."

        if isinstance(node, ast.Name) and (
            node.id in FORBIDDEN_NAMES or node.id.startswith("__")
        ):
            return f"Línea {line}: no se puede usar «{node.id}»."
        if isinstance(node, ast.Attribute) and (
            node.attr in FORBIDDEN_ATTRIBUTES
            or node.attr.startswith(FORBIDDEN_ATTRIBUTE_PREFIXES)
        ):
            return f"Línea {line}: no se puede usar «.{node.attr}»."
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "st"
            and node.attr not in ALLOWED_ST | ST_EXTRAS
        ):
            return f"Línea {line}: las aplicaciones no pueden usar «st.{node.attr}»."
        if isinstance(node, ast.keyword) and node.arg in FORBIDDEN_KEYWORDS:
            return f"Línea {line}: no se puede usar «{node.arg}»."
        if isinstance(node, ast.alias) and node.asname and node.asname.startswith("_"):
            return f"Línea {line}: no se puede usar «{node.asname}»."
    return None


def _public_namespace(module):
    """A module without its private names and without other modules inside it."""
    return SimpleNamespace(
        **{
            name: value
            for name, value in vars(module).items()
            if not name.startswith("_") and not isinstance(value, ModuleType)
        }
    )


def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    root = name.split(".")[0]
    if level or root not in ALLOWED_MODULES:
        raise ImportError(f"No se puede importar «{name}».")
    return _public_namespace(importlib.import_module(name if fromlist else root))


class _AppState:
    """st.session_state for one app: every key gets the app's prefix."""

    def __init__(self, prefix):
        object.__setattr__(self, "_prefix", prefix)

    def _key(self, key):
        return f"{self._prefix}{key}"

    def __getitem__(self, key):
        return st.session_state[self._key(key)]

    def __setitem__(self, key, value):
        st.session_state[self._key(key)] = value

    def __delitem__(self, key):
        del st.session_state[self._key(key)]

    def __contains__(self, key):
        return self._key(key) in st.session_state

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key) from None

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        del self[key]

    def get(self, key, default=None):
        return self[key] if key in self else default

    def setdefault(self, key, default=None):
        if key not in self:
            self[key] = default
        return self[key]

    def pop(self, key, *default):
        return st.session_state.pop(self._key(key), *default)

    def keys(self):
        return [
            key[len(self._prefix) :]
            for key in st.session_state.keys()
            if isinstance(key, str) and key.startswith(self._prefix)
        ]

    def items(self):
        return [(key, self[key]) for key in self.keys()]


def _check_media(value):
    if isinstance(value, dict):
        value = list(value.values())
    if isinstance(value, (list, tuple)):
        for item in value:
            _check_media(item)
    elif isinstance(value, str) and not value.startswith(WEB_PREFIXES):
        raise GuardrailError(
            "st.image, st.audio y st.video solo aceptan direcciones web o datos, no ficheros."
        )


def _html_component(html, width=None, height=None, scrolling=False):
    """st.components.v1.html, but isolated from Yahoraque.

    The real one runs the JavaScript with access to the page that shows it,
    so an app could act as its viewer (for example, the admin). A data: URL
    gets its own origin in the browser.
    """
    src = "data:text/html;base64," + base64.b64encode(html.encode()).decode()
    return st.iframe(src, width=width or "stretch", height=height or HTML_DEFAULT_HEIGHT)


class _Streamlit:
    """`st` and its containers (columns, tabs, forms…) limited to ALLOWED_ST."""

    def __init__(self, target, prefix, state):
        self._target = target
        self._prefix = prefix
        self.session_state = state
        if target is st:
            self.components = SimpleNamespace(v1=SimpleNamespace(html=_html_component))

    def _wrap(self, value):
        if isinstance(value, (list, tuple)):
            return [self._wrap(item) for item in value]
        if isinstance(value, DeltaGenerator):
            return _Streamlit(value, self._prefix, self.session_state)
        return value

    def __getattr__(self, name):
        if name not in ALLOWED_ST:
            raise AttributeError(f"Las aplicaciones no pueden usar st.{name}.")
        function = getattr(self._target, name)

        def call(*args, **kwargs):
            # Also at run time: **{"unsafe_" + "allow_javascript": True} passes check().
            if FORBIDDEN_KEYWORDS & kwargs.keys():
                raise GuardrailError("Las aplicaciones no pueden ejecutar JavaScript en la página.")
            if name in MEDIA_FUNCTIONS:
                _check_media([*args[:1], *(kwargs.get(arg) for arg in MEDIA_ARGUMENTS)])
            if kwargs.get("key") is not None:
                kwargs["key"] = f"{self._prefix}{kwargs['key']}"
            if name == "form" and args:
                args = (f"{self._prefix}{args[0]}", *args[1:])
            return self._wrap(function(*args, **kwargs))

        return call

    def __enter__(self):
        self._target.__enter__()
        return self

    def __exit__(self, *exc_info):
        return self._target.__exit__(*exc_info)


def run(code, app_id):
    """Execute an app. Raises GuardrailError if check() rejects it."""
    problem = check(code)
    if problem:
        raise GuardrailError(problem)
    prefix = f"app_{app_id}_"
    app_st = _Streamlit(st, prefix, _AppState(prefix))
    app_globals = {
        "__builtins__": {**SAFE_BUILTINS, "__import__": _safe_import},
        "__name__": "__app__",
        "st": app_st,
    }
    exec(compile(code, "<app>", "exec"), app_globals)
