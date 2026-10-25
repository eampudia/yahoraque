"""Run Yahoraque as on Streamlit Cloud, where the server does not see cookies.

docker compose run -d --name yahoraque-cloudlike app streamlit run tests/cloud_like_app.py \
    --server.port=8502 --server.address=0.0.0.0
docker compose --profile test run --rm -e APP_URL=http://yahoraque-cloudlike:8502 e2e python e2e_session.py
"""

import sys

import streamlit as st

sys.path.insert(0, "/app")

type(st.context).cookies = property(lambda self: {})
exec(open("/app/init.py").read(), {"__file__": "/app/init.py", "__name__": "__main__"})
