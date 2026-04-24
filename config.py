import streamlit as st

DB_HOST = st.secrets["mysql.railway.internal"]
DB_PORT = int(st.secrets["3306"])
DB_USER = st.secrets["root"]
DB_PASSWORD = st.secrets["RjppinauDqPuZfmRjqPjCmkVoRUbhxIB"]
DB_NAME = st.secrets["railway"]

