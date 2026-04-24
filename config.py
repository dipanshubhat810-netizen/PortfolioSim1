import streamlit as st

DB_HOST = st.secrets["DB_HOST"]
DB_PORT = int(st.secrets["DB_PORT"])
DB_USER = st.secrets["DB_USER"]
DB_PASSWORD = st.secrets["DB_PASSWORD"]
DB_NAME = st.secrets["DB_NAME"]

RISK_FREE_RATE = 0.06
TOP_ASSETS_PER_SECTOR = 5
DEFAULT_CORRELATION = 0.25
