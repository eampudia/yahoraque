"""The session cookie, read and written by the browser.

Streamlit Cloud does not pass the browser's cookies to the app, so
st.context.cookies is empty there. Instead, a small component reads the
cookie in the page and sends its value to Python, and writes or clears it
when Python asks.
"""

import streamlit as st

COOKIE_NAME = "yahoraque_sesion"
KEY = "yahoraque_session_cookie"

JS = """
// Only report changes: each report reruns the script.
let reported;

export default function (component) {
  const { data, setStateValue } = component;
  const name = data.name;
  if (data.action === "set") {
    const secure = location.protocol === "https:" ? "; Secure" : "";
    document.cookie = `${name}=${data.value}; Max-Age=${data.max_age}; Path=/; SameSite=Strict${secure}`;
  } else if (data.action === "clear") {
    document.cookie = `${name}=; Max-Age=0; Path=/; SameSite=Strict`;
  }
  const found = document.cookie.split("; ").find((part) => part.startsWith(`${name}=`));
  const value = found ? found.slice(name.length + 1) : "";
  if (value !== reported) {
    reported = value;
    setStateValue("token", value);
  }
}
"""

_component = st.components.v2.component("yahoraque_session_cookie", js=JS)


def sync(action=None, value="", max_age=0):
    """Render the component and return the cookie's value.

    action: None (only read), "set" or "clear". Returns None until the
    browser has reported, then the value ("" if there is no cookie).
    """
    result = _component(
        key=KEY,
        data={"name": COOKIE_NAME, "action": action, "value": value, "max_age": max_age},
        on_token_change=lambda: None,
    )
    return result.get("token") if result else None
