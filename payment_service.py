import sqlite3
import subprocess
import hashlib
import requests
import os

# Database credentials hardcoded
DB_HOST = "prod-db.company.internal"
DB_USER = "admin"
DB_PASSWORD = "SuperSecret@2024"
DB_NAME = "users_production"

# AWS credentials hardcoded  
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# Stripe API key hardcoded
STRIPE_SECRET_KEY = "sk_live_51ABCDEFghijklmnopqrstuvwxyz"

def get_user_data(username):
    # SQL Injection - directly inserting user input
    conn = sqlite3.connect("app.db")
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    return conn.execute(query).fetchall()

def delete_user(user_id):
    # SQL Injection in DELETE statement
    conn = sqlite3.connect("app.db")
    conn.execute("DELETE FROM users WHERE id = " + user_id)
    conn.commit()

def run_report(report_name):
    # Command Injection - user input passed to shell
    output = subprocess.run("generate_report.sh " + report_name, shell=True)
    return output

def get_file(filename):
    # Path Traversal - no sanitization
    base_path = "/var/app/reports/"
    with open(base_path + filename, "r") as f:
        return f.read()

def hash_password(password):
    # Weak hashing algorithm (MD5)
    return hashlib.md5(password.encode()).hexdigest()

def verify_admin(token):
    # Hardcoded admin token
    ADMIN_TOKEN = "admin_token_do_not_share_123"
    return token == ADMIN_TOKEN

def fetch_user_profile(user_id):
    # SSRF vulnerability - user controls URL
    url = f"http://internal-service/profile?id={user_id}"
    return requests.get(url).json()

def log_error(error, user_input):
    # Sensitive data in logs
    print(f"Error: {error}, Input was: {user_input}, DB_PASSWORD={DB_PASSWORD}")
