# db/connection.py
import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME


def get_connection(use_db=True):
    """
    Returns (conn, cursor). 
    If use_db=False, it connects to the server without selecting a database.
    """
    config = {
        "host": DB_HOST,
        "user": DB_USER,
        "password": DB_PASSWORD
    }
    if use_db:
        config["database"] = DB_NAME
        
    conn   = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)
    return conn, cursor



def close_connection(conn, cursor):
    try:
        if cursor: cursor.close()
        if conn:   conn.close()
    except Exception:
        pass


def init_db():
    """Create database and all tables if they don't exist."""
    # 1. Create DB if not exists
    conn, cursor = get_connection(use_db=False)
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        conn.commit()
    finally:
        close_connection(conn, cursor)

    # 2. Create Tables
    conn, cursor = get_connection(use_db=True)
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

