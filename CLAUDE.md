# yahoraque

Yahoraque lets teachers with no programming knowledge create, by chatting with an AI, small web apps for their day to day (e.g. a language teacher's essay corrector that reads handwritten photos), and share them.

## Stack
- Language: Python
- Production runtime: Streamlit (`streamlit run app.py`). Streamlit Cloud was deployed with `init.py`, which only runs `app.py`: keep both.
- Local development and testing: Docker only

## Rules

### Local environment
- Never install packages or tools on the host machine (no `pip install`, `brew install`, etc.).
- Run everything inside Docker: the app, tests, linters and one-off scripts.
- If a Dockerfile or `docker-compose.yml` is missing or needs a change, create or update it instead of working around it on the host.

### Dependencies
- Every new library goes into `requirements.txt`, pinned to a version (e.g. `pandas==2.2.3`).
- Rebuild the Docker image after changing `requirements.txt`.

### Secrets
- Never hardcode passwords, API keys or tokens in code, tests or Docker files.
- Locally, read them from environment variables loaded from `.env`. Keep `.env` in `.gitignore`, and keep a `.env.example` with the variable names and no real values.
- In production, use Streamlit secrets (`st.secrets` / `.streamlit/secrets.toml`, which also stays out of git).

### Git
- Never commit or push without asking me first. Show me what will be committed and wait for my OK.
### Plus
- If you do something right and I praise you, please add it to this file, (before asking me)
- When updating `especificacion.md`: turn ideas into concrete, testable rules, keep the sections consistent (no duplicates, add acceptance criteria), and point out ambiguous wording instead of guessing silently. 
- When production fails, reproduce it locally under the same conditions (same model, same input) before blaming the AI or the quota: the cause may be our code (e.g. the ``` extraction bug). Document the failure and the fix as an edge case in `especificacion.md` and in "Prueba y mejora" of the README.
