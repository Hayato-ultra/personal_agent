import sqlite3
import json
from datetime import datetime
from pathlib import Path


DB_PATH = Path(__file__).parent / "memory.db"


class ProceduralMemory:
    def __init__(self, db_path=DB_PATH):
        self.db = sqlite3.connect(db_path)
        self.db.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS procedures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                triggers TEXT,
                steps TEXT NOT NULL,
                requirements TEXT,
                success_condition TEXT,
                confidence REAL DEFAULT 0.5,
                usage_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TEXT,
                updated_at TEXT
            )
        """)

        self.db.commit()

    def store(
        self,
        name,
        description,
        triggers,
        steps,
        requirements=None,
        success_condition=None,
        confidence=0.5
    ):
        now = datetime.now().isoformat()

        self.db.execute("""
            INSERT INTO procedures (
                name,
                description,
                triggers,
                steps,
                requirements,
                success_condition,
                confidence,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                description = excluded.description,
                triggers = excluded.triggers,
                steps = excluded.steps,
                requirements = excluded.requirements,
                success_condition = excluded.success_condition,
                confidence = excluded.confidence,
                updated_at = excluded.updated_at
        """, (
            name,
            description,
            json.dumps(triggers),
            json.dumps(steps),
            json.dumps(requirements or []),
            success_condition,
            confidence,
            now,
            now
        ))

        self.db.commit()

    def get(self, name):
        row = self.db.execute("""
            SELECT * FROM procedures
            WHERE name = ?
            AND status = 'active'
        """, (name,)).fetchone()

        if not row:
            return None

        return self._deserialize(row)

    def search(self, query):
        query = f"%{query.lower()}%"

        rows = self.db.execute("""
            SELECT *
            FROM procedures
            WHERE status = 'active'
            AND (
                LOWER(name) LIKE ?
                OR LOWER(description) LIKE ?
                OR LOWER(triggers) LIKE ?
            )
            ORDER BY confidence DESC, usage_count DESC
        """, (query, query, query)).fetchall()

        return [self._deserialize(row) for row in rows]

    def record_success(self, procedure_id):
        self.db.execute("""
            UPDATE procedures
            SET
                usage_count = usage_count + 1,
                success_count = success_count + 1,
                confidence = MIN(1.0, confidence + 0.05),
                updated_at = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), procedure_id))

        self.db.commit()

    def record_failure(self, procedure_id):
        self.db.execute("""
            UPDATE procedures
            SET
                usage_count = usage_count + 1,
                failure_count = failure_count + 1,
                confidence = MAX(0.0, confidence - 0.10),
                updated_at = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), procedure_id))

        self.db.commit()

    def _deserialize(self, row):
        data = dict(row)

        data["triggers"] = json.loads(data["triggers"])
        data["steps"] = json.loads(data["steps"])
        data["requirements"] = json.loads(data["requirements"])

        return data

    def close(self):
        self.db.close()