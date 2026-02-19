import sqlite3


def get_user(user_id):
    # SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"
    conn = sqlite3.connect("db.sqlite")
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchone()


# Hardcoded secrets
API_KEY = "sk-1234567890abcdef"
PASSWORD = "admin123"
# Test update
# Updated
# Test improved titles
# Production test
# Production test v2
# Test production deployment
# New test Thu Feb 19 00:03:45 PST 2026
