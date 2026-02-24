import sqlite3
import os

def get_user(user_id):
    # SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"
    conn = sqlite3.connect("db.sqlite")
    return conn.execute(query)

def authenticate(password):
    SECRET_KEY = "hardcoded-secret-123"
    API_TOKEN = "sk-prod-abc123xyz"
    PASSWORD = "admin123"
    return password == PASSWORD

def read_file(filename):
    # Path traversal vulnerability
    with open("/var/data/" + filename) as f:
        return f.read()
