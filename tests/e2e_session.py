"""Browser test: the session survives a page reload, and "Salir" ends it.

Uses guest access, so it writes nothing to storage.
Run: docker compose --profile test run --rm e2e python e2e_session.py
Options (environment): APP_URL, BROWSER (chromium, firefox or webkit).
"""

import os

from playwright.sync_api import expect, sync_playwright

APP_URL = os.environ.get("APP_URL", "http://localhost:8501")
BROWSER = os.environ.get("BROWSER", "chromium")
TIMEOUT_MS = 60_000
# On Streamlit Cloud the app runs in an iframe inside the page.
CLOUD_FRAME = "iframe[title='streamlitApp']"


def app_root(page):
    if page.locator(CLOUD_FRAME).count():
        return page.frame_locator(CLOUD_FRAME)
    return page


def is_visible(locator):
    try:
        expect(locator).to_be_visible(timeout=10_000)
        return True
    except AssertionError:
        return False


with sync_playwright() as playwright:
    browser = getattr(playwright, BROWSER).launch()
    page = browser.new_page()
    page.set_default_timeout(TIMEOUT_MS)
    print(f"{BROWSER} en {APP_URL}")

    page.goto(APP_URL)
    page.wait_for_timeout(5000)
    app = app_root(page)
    app.get_by_role("button", name="Entrar como invitado").click()
    expect(app.get_by_test_id("stSidebar").get_by_text("Salir")).to_be_visible()
    # Give the browser time to run the script that stores the cookie.
    page.wait_for_timeout(3000)
    names = [cookie["name"] for cookie in page.context.cookies()]
    print("  cookie tras entrar:", "yahoraque_sesion" in names)

    page.reload()
    page.wait_for_timeout(5000)
    app = app_root(page)
    still_in = is_visible(app.get_by_test_id("stSidebar").get_by_text("Salir"))
    print("  tras recargar sigue dentro:", still_in)

    if still_in:
        app.get_by_test_id("stSidebar").get_by_role("button", name="Salir").click()
        expect(app.get_by_role("button", name="Entrar como invitado")).to_be_visible()
        page.wait_for_timeout(3000)
        page.reload()
        page.wait_for_timeout(5000)
        app = app_root(page)
        print(
            "  tras salir y recargar, pantalla de acceso:",
            is_visible(app.get_by_role("button", name="Entrar como invitado")),
        )

    browser.close()
