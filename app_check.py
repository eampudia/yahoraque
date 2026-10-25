"""Check that a generated app starts without errors.

The app runs in a separate process with no secrets in its environment and a
time limit, so a broken or endless app cannot block or leak from Yahoraque.
Run as a script, it reads the code from stdin and prints a JSON result.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent
SCRIPT_TIMEOUT = 20
PROCESS_TIMEOUT = 30
RUNNER = "import guardrails\nguardrails.run({code!r}, 'check')\n"


def test_run(code):
    """Return a description of the error, or None if the app starts fine."""
    env = {"PATH": os.environ.get("PATH", ""), "HOME": tempfile.gettempdir(), "PYTHONPATH": str(ROOT)}
    with tempfile.TemporaryDirectory() as workdir:
        try:
            result = subprocess.run(
                [sys.executable, str(ROOT / "app_check.py")],
                input=code,
                capture_output=True,
                text=True,
                env=env,
                # Away from the project, so no .streamlit/secrets.toml is found.
                cwd=workdir,
                timeout=PROCESS_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            return "La aplicación tarda demasiado en arrancar (¿hay un bucle infinito?)."
    try:
        return json.loads(result.stdout.strip().splitlines()[-1])["error"]
    except (IndexError, KeyError, ValueError):
        return f"La comprobación ha fallado: {result.stderr[-1000:]}"


def _main():
    from streamlit.testing.v1 import AppTest

    code = sys.stdin.read()
    try:
        app = AppTest.from_string(RUNNER.format(code=code), default_timeout=SCRIPT_TIMEOUT)
        app.run()
        error = None
        if app.exception:
            exception = app.exception[0]
            error = f"{exception.message}\n{''.join(exception.stack_trace)[-2000:]}"
    except RuntimeError:
        error = "La aplicación tarda demasiado en arrancar (¿hay un bucle infinito?)."
    print(json.dumps({"error": error}), flush=True)
    # Do not wait for an app thread that may still be running.
    os._exit(0)


if __name__ == "__main__":
    _main()
