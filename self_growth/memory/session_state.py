# session_state.py

import sqlite3
from datetime import datetime
from raven_path_initializer import set_project_root, get_full_path

set_project_root()
DB_PATH = get_full_path("self_growth/memory/session_state.db")

def init_session_db():
    print("[DEBUG] Initializing session state DB...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            active_mode TEXT,
            emotion_tags TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("[DEBUG] Session state DB initialized at:", DB_PATH)

def save_session_state(active_mode, emotion_tags):
    timestamp = datetime.now().isoformat()
    print(f"[DEBUG] Saving session state @ {timestamp}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sessions (timestamp, active_mode, emotion_tags)
        VALUES (?, ?, ?)
    ''', (timestamp, active_mode, ",".join(emotion_tags)))
    conn.commit()
    conn.close()
    print("[DEBUG] Session state saved.")

def fetch_last_session():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, active_mode, emotion_tags FROM sessions
        ORDER BY id DESC LIMIT 1
    ''')
    row = cursor.fetchone()
    conn.close()

    if row:
        print("[DEBUG] Retrieved session:", row)
        return {
            "timestamp": row[0],
            "active_mode": row[1],
            "emotion_tags": row[2].split(",")
        }
    else:
        print("[DEBUG] No session records found.")
        return None

if __name__ == "__main__":
    init_session_db()

