# db/connection.py
import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME


def get_connection():
    conn   = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
    )
    cursor = conn.cursor(dictionary=True)
    return conn, cursor


def close_connection(conn, cursor):
    try:
        if cursor: cursor.close()
        if conn:   conn.close()
    except Exception:
        pass


def init_db():
    """Create all tables if they don't exist. Called once at startup."""
    conn, cursor = get_connection()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            INT PRIMARY KEY AUTO_INCREMENT,
                username      VARCHAR(100) UNIQUE NOT NULL,
                email         VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id                 INT PRIMARY KEY AUTO_INCREMENT,
                user_id            INT NOT NULL,
                name               VARCHAR(100) NOT NULL,
                age                INT,
                occupation         VARCHAR(100),
                income             DECIMAL(15,2),
                investment_amount  DECIMAL(15,2),
                risk_capacity      INT,
                investment_horizon VARCHAR(50),
                investment_goal    VARCHAR(200),
                created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_portfolios (
                id             INT PRIMARY KEY AUTO_INCREMENT,
                user_id        INT NOT NULL,
                profile_id     INT NOT NULL,
                label          VARCHAR(100),
                portfolio_json TEXT NOT NULL,
                exp_return     DECIMAL(6,4),
                variance       DECIMAL(8,6),
                risk_type      VARCHAR(20),
                created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
                FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
    finally:
        close_connection(conn, cursor)
