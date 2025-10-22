import os
import json
import requests
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

database_path = os.path.join(os.path.dirname(__file__), 'wonder_bot_database.db')

# Get a database connection
def get_db_connection():
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
def create_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_packets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            subtopics TEXT NOT NULL,
            grade_level TEXT NOT NULL,
            num_problems INTEGER NOT NULL,
            pdf_path TEXT NOT NULL,
            public BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# Add a new user
def add_user(email, username, password):
    try:
        password_hash = generate_password_hash(password)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (email, username, password_hash)
            VALUES (?, ?, ?)
        ''', (email, username, password_hash))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

# Add a new learning packet
def add_learning_packet(user_id, topic, subtopics, grade_level, num_problems, pdf_path):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO learning_packets (user_id, topic, subtopics, grade_level, num_problems, pdf_path)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, topic, json.dumps(subtopics), grade_level, num_problems, pdf_path))
    conn.commit()
    conn.close()

# Retrieve learning packets for a user
def get_user_learning_packets(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM learning_packets WHERE user_id = ?
    ''', (user_id,))
    packets = cursor.fetchall()
    conn.close()
    return packets

# Retrieve all public learning packets
def get_all_public_learning_packets():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM learning_packets WHERE public = 1
    ''')
    packets = cursor.fetchall()
    conn.close()
    return packets

# Updates packet visibility
def update_packet_visibility(packet_id, is_public):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE learning_packets SET public = ? WHERE id = ?
    ''', (is_public, packet_id))
    conn.commit()
    conn.close()

# Validate user credentials
def validate_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    # Retrieve hashed password for the given username
    cur.execute("SELECT password_hash, id FROM users WHERE username = ?", (username,))
    user_row = cur.fetchone()
    conn.close()

    # Checks hashed user password against database
    if user_row and check_password_hash(user_row['password_hash'], password):
        return user_row['id']
    return None

# Gets username
def get_username(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username FROM users WHERE id = ?
    ''', (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return user['username']
    return None