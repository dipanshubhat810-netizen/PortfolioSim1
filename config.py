import streamlit as st

# -------------------------
# Database config
# -------------------------
DB_HOST = st.secrets["DB_HOST"]
DB_PORT = int(st.secrets.get("DB_PORT", 3306))
DB_USER = st.secrets["DB_USER"]
DB_PASSWORD = st.secrets["DB_PASSWORD"]
DB_NAME = st.secrets["DB_NAME"]

# -------------------------
# Portfolio config
# -------------------------
RISK_FREE_RATE        = 0.03
TOP_ASSETS_PER_SECTOR = 2
DEFAULT_CORRELATION   = 0.10
