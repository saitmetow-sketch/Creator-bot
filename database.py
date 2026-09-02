import sqlite3
import os

DB_NAME = "creator_bot.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        full_name TEXT,
        username TEXT,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        referrer_id INTEGER
    )
    """)
    
    # Created Bots
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS created_bots (
        bot_id INTEGER PRIMARY KEY,
        owner_id INTEGER,
        bot_name TEXT,
        bot_username TEXT,
        bot_token TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        is_active INTEGER DEFAULT 1,
        paid_extensions INTEGER DEFAULT 0
    )
    """)
    
    # Admins
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        user_id INTEGER PRIMARY KEY
    )
    """)
    
    # Mandatory Channels
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mandatory_channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel_id TEXT,
        channel_username TEXT,
        channel_link TEXT
    )
    """)
    
    # Request Channels
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS request_channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel_id TEXT,
        channel_link TEXT
    )
    """)
    
    # Referrals
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER,
        referred_id INTEGER UNIQUE
    )
    """)
    
    # Extensions log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS extensions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bot_id INTEGER,
        days_added INTEGER,
        extended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()
