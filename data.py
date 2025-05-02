# Database initialization function
import sqlite3
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database
init_db()

from datetime import datetime

# Add this function to initialize the contacts table
def init_contacts_table():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    

    # Create contacts table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'unread'
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database tables
def get_all_users():
    """Fetch all users from the database."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return users

# Example usage:
all_users = get_all_users()
for user in all_users:
     print(f"ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")

get_all_users()