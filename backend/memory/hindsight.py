# Filename: backend/memory/hindsight.py

import sqlite3
import os

class HindsightMemoryDB:
    def __init__(self, db_path: str = "data/hindsight_memory.db"):
        """
        Initialize the SQLite database.
        Creates a permanent storage file inside our data/ directory to track incidents.
        """
        self.db_path = db_path
        # Ensure the directory path exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._initialize_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _initialize_table(self):
        """Creates our historical incident tracking matrix if it doesn't exist yet."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_signature TEXT UNIQUE,
                    occurrence_count INTEGER DEFAULT 1,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_by TEXT DEFAULT 'DevOps Senior Agent'
                )
            """)
            conn.commit()

    def check_and_record_incident(self, error_signature: str) -> dict:
        """
        Queries historical memory records. 
        If a matching incident signature is found, increments the tracking counter.
        If it's a completely new issue, registers it fresh into historical tables.
        """
        # Clean the signature slightly to avoid spacing issues
        clean_signature = error_signature.strip()[:150]
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Look up if this error signature exists in our memory banks
            cursor.execute("SELECT occurrence_count, resolved_by FROM incidents WHERE error_signature = ?", (clean_signature,))
            row = cursor.fetchone()
            
            if row:
                # Historical matching entry found! Increment its counter
                new_count = row[0] + 1
                resolved_by = row[1]
                cursor.execute("""
                    UPDATE incidents 
                    SET occurrence_count = ?, last_seen = CURRENT_TIMESTAMP 
                    WHERE error_signature = ?
                """, (new_count, clean_signature))
                is_repeated = True
            else:
                # Brand new issue! Insert it fresh with a default fallback resolver
                new_count = 1
                resolved_by = "Automated AI Fix Patch v1.2"
                cursor.execute("""
                    INSERT INTO incidents (error_signature, occurrence_count, resolved_by) 
                    VALUES (?, ?, ?)
                """, (clean_signature, new_count, resolved_by))
                is_repeated = False
                
            conn.commit()
            
            return {
                "is_repeated_incident": is_repeated,
                "historical_occurrence_count": new_count,
                "assigned_resolution_owner": resolved_by
            }