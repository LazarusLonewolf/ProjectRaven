# emotion_recall.py

import sqlite3
from datetime import datetime
from raven_path_initializer import set_project_root, get_full_path

set_project_root()

# Load Raven training data for contextual insight
RAVEN_TRAINING_DATA_PATH = get_full_path('vaults/raven_training_data.txt')
try:
    with open(RAVEN_TRAINING_DATA_PATH, 'r', encoding='utf-8') as file:
        raven_ethos_reference = file.read()
except Exception as e:
    print(f'[ERROR] Failed to load Raven training data: {e}')
    raven_ethos_reference = ''

DB_PATH = get_full_path("self_growth/memory/emotion_log.db")

def init_emotion_log_db():
    print("[DEBUG] Initializing emotion log DB...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emotion_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            emotion TEXT,
            intensity INTEGER,
            context TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("[DEBUG] Emotion log DB initialized.")

def log_emotion(emotion, intensity, context):
    timestamp = datetime.now().isoformat()
    print(f"[DEBUG] Logging emotion @ {timestamp}: {emotion} ({intensity})")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO emotion_log (timestamp, emotion, intensity, context)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, emotion, intensity, context))
    conn.commit()
    conn.close()
    print("[DEBUG] Emotion logged.")

def recall_recent_emotions(limit=5):
    print(f"[DEBUG] Recalling last {limit} emotions...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, emotion, intensity, context FROM emotion_log
        ORDER BY id DESC LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows
