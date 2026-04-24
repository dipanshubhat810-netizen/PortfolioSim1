# modules/auth.py
import bcrypt
import streamlit as st
from db.connection import get_connection, close_connection


def _hash(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def _verify(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(pw.encode(), hashed.encode())


def register_user(username: str, email: str, password: str):
    """Returns (True, user_id, 'ok') or (False, None, error_msg)"""
    if len(password) < 6:
        return False, None, "Password must be at least 6 characters."
    conn, cursor = get_connection()
    try:
        cursor.execute(
            "SELECT id FROM users WHERE username=%s OR email=%s", (username, email)
        )
        if cursor.fetchone():
            return False, None, "Username or email already taken."
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s,%s,%s)",
            (username, email, _hash(password))
        )
        conn.commit()
        return True, cursor.lastrowid, "ok"
    except Exception as e:
        return False, None, str(e)
    finally:
        close_connection(conn, cursor)


def login_user(username: str, password: str):
    """Returns (True, user_dict) or (False, error_msg)"""
    conn, cursor = get_connection()
    try:
        cursor.execute(
            "SELECT id, username, email, password_hash FROM users WHERE username=%s",
            (username,)
        )
        row = cursor.fetchone()
        if not row:
            return False, "Username not found."
        if not _verify(password, row["password_hash"]):
            return False, "Incorrect password."
        return True, {"id": row["id"], "username": row["username"], "email": row["email"]}
    except Exception as e:
        return False, str(e)
    finally:
        close_connection(conn, cursor)


def is_logged_in() -> bool:
    return bool(st.session_state.get("user"))


def current_user() -> dict:
    return st.session_state.get("user")


def set_session(user: dict):
    st.session_state["user"] = user


def logout():
    for k in ["user", "view", "selected_profile_id", "preview"]:
        st.session_state.pop(k, None)
