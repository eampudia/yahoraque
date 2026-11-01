# yahoraque

Yahoraque lets teachers with no programming knowledge create, by chatting with an AI, small web apps for their day to day (e.g. a language teacher's essay corrector that reads handwritten photos), and share them.

The user is a teacher, not a developer. Every decision is judged by that: fewer steps, plain words, nothing technical on screen. The source of truth for behaviour is `especificacion.md`; read the relevant section before changing a feature.

## Stack
- Language: Python 3.12
- Production runtime: Streamlit (`streamlit run app.py`) on Streamlit Community Cloud, https://yahoraque.streamlit.app/. Streamlit Cloud was deployed with `init.py`, which only runs `app.py`: keep both.
- AI: Gemini free tier through `google-genai`. The model is never hardcoded: `llm.py` lists the available models, ranks them and falls back to the next one.
- Storage: GitHub. User data lives in the `datos` branch, never in `master` (a commit to `master` redeploys the app).
- Local development and testing: Docker only

## Project map
- `app.py`: pages, menu and session. Every page function lives here.
- `analyst.py` / `developer.py`: the two AI roles that turn a chat into requirements and requirements into code.
- `prompts/*.md`: the AI's instructions (analista, desarrollador, ia_apps). Change the wording there, not in Python.
- `guardrails.py`: checks and runs generated apps with a limited `st`, safe builtins and per-app keys. `app_check.py` test-starts an app in a separate process with no secrets.
- `app_ai.py`: the `ia()` function generated apps get. The API key stays on the server.
- `apps.py`: one app per user, its versions (last 10) and public apps.
- `auth.py`: name + PIN, guest and admin; signed session token. `session_cookie.py` keeps it in the browser.
- `usage.py`: daily usage registry in `uso/<UTC date>.json` (calls, failures, resting models, limits).
- `storage.py`: local disk (`.data/`) or GitHub, chosen by `STORAGE_MODE`.
- `waiting.py`: the funny phrases while the AI works. `app_theme.py`: Pico CSS, Yahoraque's look and the allowed JS libraries.
- `tests/`: Playwright browser tests (`e2e_session.py`) and `cloud_like_app.py`, which runs the app without cookies, as on Streamlit Cloud.

## Running and testing
- App: `docker compose up` → http://localhost:8501
- Browser tests: `docker compose --profile test run --rm e2e python e2e_session.py` (`BROWSER=firefox|webkit` for the others). For the Streamlit Cloud case, see the header of `tests/cloud_like_app.py`.
- Page tests use `streamlit.testing.v1.AppTest` inside the app container.
- Tests must never write to the real `datos` branch: run them with `STORAGE_MODE=local`.
- Check a change in the real app, not only in tests, and in production when it touches session, cookies or links.

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
- Values in `.env` may have spaces around `=` and a trailing `\r`: strip them when a shell script reads them.

### Generated apps (security)
- Never loosen the guardrails to make an app work: fix the prompt or the error message the AI gets instead.
- Generated code must never reach secrets, files, the network from Python, or Yahoraque's session state.
- The Gemini key never leaves the server. Apps only get answers through `ia()`, with its daily limit.

### Language and style
- Everything the user sees is in Spanish, in plain words for a teacher. Messages say what happened and what to do next.
- Code, comments and docstrings are in English. Match the surrounding code.
- Replies to me are in Spanish.

### Git
- Never commit or push without asking me first. Show me what will be committed and wait for my OK.

### Documentation
- When updating `especificacion.md`: turn ideas into concrete, testable rules, keep the sections consistent (no duplicates, add acceptance criteria), and point out ambiguous wording instead of guessing silently.
- A feature is not done until `especificacion.md` (rules, acceptance criteria, edge cases) and, if the user can see it, the README are updated.

### Plus
- If you do something right and I praise you, please add it to this file, (before asking me)
- When production fails, reproduce it locally under the same conditions (same model, same input) before blaming the AI or the quota: the cause may be our code (e.g. the ``` extraction bug). Document the failure and the fix as an edge case in `especificacion.md` and in "Prueba y mejora" of the README.

## Lessons learned
- Streamlit Cloud does not pass browser cookies to the app (`st.context.cookies` is empty): the session is read in the browser by `session_cookie.py`.
- AI apps contain ``` in their own code: extract the generated code up to the last fence, not the first.
- The free quota is shared by every user: count usage in `usage.py`, which persists in `datos` and survives restarts. Google has no API for the remaining quota.
- Each GitHub read or write is an API call: cache reads (`st.cache_data`) and keep per-session copies.
