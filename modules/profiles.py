# modules/profiles.py
from db.connection import get_connection, close_connection


def get_risk_label(risk: int) -> str:
    if risk <= 3:   return "conservative"
    elif risk <= 6: return "balanced"
    else:           return "aggressive"


def get_all_profiles(user_id: int):
    conn, cursor = get_connection()
    try:
        cursor.execute(
            "SELECT * FROM profiles WHERE user_id=%s ORDER BY created_at DESC",
            (user_id,)
        )
        return cursor.fetchall()
    finally:
        close_connection(conn, cursor)


def get_profile(profile_id: int, user_id: int):
    conn, cursor = get_connection()
    try:
        cursor.execute(
            "SELECT * FROM profiles WHERE id=%s AND user_id=%s",
            (profile_id, user_id)
        )
        return cursor.fetchone()
    finally:
        close_connection(conn, cursor)


def create_profile(user_id, name, age, occupation,
                   income, investment_amount, risk_capacity,
                   investment_horizon, investment_goal):
    conn, cursor = get_connection()
    try:
        cursor.execute("""
            INSERT INTO profiles
              (user_id,name,age,occupation,income,investment_amount,
               risk_capacity,investment_horizon,investment_goal)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (user_id, name, age, occupation, income, investment_amount,
              risk_capacity, investment_horizon, investment_goal))
        conn.commit()
        return True, cursor.lastrowid, "ok"
    except Exception as e:
        return False, None, str(e)
    finally:
        close_connection(conn, cursor)


def delete_profile(profile_id: int, user_id: int):
    conn, cursor = get_connection()
    try:
        cursor.execute(
            "DELETE FROM profiles WHERE id=%s AND user_id=%s",
            (profile_id, user_id)
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        close_connection(conn, cursor)
