"""Entry point kept for Streamlit Community Cloud, which was deployed with init.py.

The app itself is app.py; this runs it again on every rerun, as Streamlit would.
"""

import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).with_name("app.py")), run_name="__main__")
