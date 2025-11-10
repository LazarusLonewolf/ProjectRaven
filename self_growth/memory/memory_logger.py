import sqlite3
import time
from raven_path_initializer import set_project_root, get_full_path

set_project_root()
DB_PATH = get_full_path("self_growth/memory/raven_memory.db")

def log_memory(event_type, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS memory_log (
               timestamp TEXT,
               event_type TEXT,
               content TEXT
           )'''
    )
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO memory_log (timestamp, event_type, content) VALUES (?, ?, ?)",
              (timestamp, event_type, content))
    conn.commit()
    conn.close()
