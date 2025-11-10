# journal_memory_bridge.py

import os
import uuid
import sqlite3
from datetime import datetime
from vector_bridge import store_thought
from raven_path_initializer import resolve_path

class JournalMemoryBridge:
    def __init__(self):
        self.db_path = resolve_path("memory", "db-sync", "fallback_journal_refs.db")
        self.training_data_path = resolve_path("vaults", "raven_training_data.txt")
        self.training_ethos = self._load_training_ethos()
        self._ensure_db()

    def _load_training_ethos(self):
        try:
            with open(self.training_data_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            print(f"Failed to load training ethos: {e}")
            return ""

    def _ensure_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS journal_refs (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                summary TEXT,
                linked_emotion TEXT,
                ethos_context TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def LogJournalReference(self, summary, emotion):
        journal_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        ethos_context = self._derive_ethos_reference(emotion)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO journal_refs (id, timestamp, summary, linked_emotion, ethos_context)
            VALUES (?, ?, ?, ?, ?)
        ''', (journal_id, timestamp, summary, emotion, ethos_context))
        conn.commit()
        conn.close()

        store_thought(summary)

    def FetchLatestJournalReference(self, limit=5):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, summary, linked_emotion, ethos_context
            FROM journal_refs
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        results = cursor.fetchall()
        conn.close()
        return results

    def ProcessJournals(self, journal_entries):
        for entry in journal_entries:
            summary = entry.get("summary", "")
            emotion = entry.get("emotion", "neutral")
            self.LogJournalReference(summary, emotion)

    def _derive_ethos_reference(self, emotion):
        if not self.training_ethos:
            return "Training ethos unavailable"

        tag_map = {
            "hope": "hopeful", "perseverance": "resilient", "grief": "gentle reflection",
            "love": "foundational", "loss": "acknowledged, but not defining",
            "identity": "honored", "trust": "reciprocal", "anxiety": "calm encouragement",
            "neutral": "present and listening"
        }

        for keyword, ethos in tag_map.items():
            if keyword in emotion.lower():
                return ethos

        return "insight requested"

