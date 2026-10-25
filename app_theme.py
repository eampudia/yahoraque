"""Yahoraque's look for the apps, and the JavaScript libraries they may load.

Every app page gets Pico CSS and the Yahoraque theme (the logo's colours and
rounded fonts) injected into its <head>, so apps look like part of the
platform and the AI writes less CSS. Apps may only load the libraries in
LIBRARIES, with these exact URLs and versions.
"""

import re

PICO_URL = "https://cdn.jsdelivr.net/npm/@picocss/pico@2.0.6/css/pico.min.css"
FONTS_URL = (
    "https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700"
    "&family=Nunito:wght@400;600;700&display=swap"
)

# What it is for -> exact URL. Shown to the AI and checked in the code.
LIBRARIES = {
    "Gráficas (Chart.js 4)": "https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js",
    "Confeti y celebraciones (canvas-confetti)": (
        "https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js"
    ),
    "Interactividad declarativa (Alpine.js 3, con defer)": (
        "https://cdn.jsdelivr.net/npm/alpinejs@3.14.1/dist/cdn.min.js"
    ),
    "Juegos, dibujo y animación (p5.js)": "https://cdn.jsdelivr.net/npm/p5@1.9.4/lib/p5.min.js",
}
# Already injected by Yahoraque; listing them in the app is harmless.
INJECTED = {PICO_URL, FONTS_URL}

THEME_CSS = """
:root {
  --yq-blue: #2f7bf5;
  --yq-green: #1cc39a;
  --yq-yellow: #fdb924;
  --yq-purple: #9a5cf6;
  --yq-navy: #13183f;
  color-scheme: light;
}
:root:not([data-theme=dark]), [data-theme=light] {
  --pico-font-family: "Nunito", system-ui, sans-serif;
  --pico-border-radius: 0.9rem;
  --pico-color: var(--yq-navy);
  --pico-h1-color: var(--yq-navy);
  --pico-h2-color: var(--yq-navy);
  --pico-h3-color: var(--yq-navy);
  --pico-primary: var(--yq-purple);
  --pico-primary-background: var(--yq-purple);
  --pico-primary-border: var(--yq-purple);
  --pico-primary-underline: rgba(154, 92, 246, 0.5);
  --pico-primary-hover: #7c3aed;
  --pico-primary-hover-background: #7c3aed;
  --pico-primary-hover-border: #7c3aed;
  --pico-primary-focus: rgba(154, 92, 246, 0.35);
  --pico-primary-inverse: #fff;
}
h1, h2, h3, h4, h5, h6, button, [role=button] {
  font-family: "Fredoka", "Nunito", system-ui, sans-serif;
}
"""

HEAD = f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>document.documentElement.setAttribute("data-theme", "light");</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="{FONTS_URL}">
<link rel="stylesheet" href="{PICO_URL}">
<style>{THEME_CSS}</style>
"""

HEAD_TAG = re.compile(r"<head[^>]*>", re.IGNORECASE)
URL_PATTERN = re.compile(r"""<(?:script|link)\b[^>]*?(?:src|href)\s*=\s*["']([^"']+)["']""", re.IGNORECASE)


def with_theme(html):
    """The page with Pico and the Yahoraque theme at the start of its <head>.

    The app's own styles come later, so they can still override the theme.
    """
    match = HEAD_TAG.search(html)
    if match:
        return html[: match.end()] + HEAD + html[match.end() :]
    return HEAD + html


def unknown_libraries(code):
    """External scripts or stylesheets in the code that are not in the kit."""
    allowed = set(LIBRARIES.values()) | INJECTED | {"https://fonts.googleapis.com"}
    return sorted({url for url in URL_PATTERN.findall(code) if url.startswith("http") and url not in allowed})
