"""SQLite schema and persistence manager for immutable design versions."""

import sqlite3
import json
import datetime
from pathlib import Path
from ..config import DEFAULT_DB_PATH, APP_NAME, APP_VERSION


class DesignStorage:
    def __init__(self, db_path: Path | str | None = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_tables()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS designs (
                    design_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    device_type TEXT NOT NULL,
                    created_at_utc TEXT NOT NULL,
                    latest_version INTEGER NOT NULL DEFAULT 1
                );

                CREATE TABLE IF NOT EXISTS design_versions (
                    version_id TEXT PRIMARY KEY,
                    design_id TEXT NOT NULL,
                    version_number INTEGER NOT NULL,
                    user_prompt TEXT,
                    device_type TEXT NOT NULL,
                    specification_json TEXT NOT NULL,
                    cad_properties_json TEXT NOT NULL,
                    validation_json TEXT NOT NULL,
                    material_candidates_json TEXT,
                    export_paths_json TEXT,
                    created_at_utc TEXT NOT NULL,
                    app_version TEXT NOT NULL,
                    FOREIGN KEY (design_id) REFERENCES designs(design_id)
                );

                CREATE TABLE IF NOT EXISTS audit_log (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    design_id TEXT NOT NULL,
                    version_number INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    timestamp_utc TEXT NOT NULL
                );
            """)
            conn.commit()

    def save_design_version(
        self,
        design_id: str,
        title: str,
        device_type: str,
        specification: dict,
        cad_properties: dict,
        validation_report: dict,
        user_prompt: str = "",
        material_candidates: list[dict] | None = None,
        export_paths: dict | None = None
    ) -> int:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with self._get_connection() as conn:
            cur = conn.execute("SELECT latest_version FROM designs WHERE design_id = ?", (design_id,))
            row = cur.fetchone()
            if row is None:
                version_num = 1
                conn.execute(
                    "INSERT INTO designs (design_id, title, device_type, created_at_utc, latest_version) VALUES (?, ?, ?, ?, ?)",
                    (design_id, title, device_type, now, 1)
                )
            else:
                version_num = row["latest_version"] + 1
                conn.execute(
                    "UPDATE designs SET latest_version = ? WHERE design_id = ?",
                    (version_num, design_id)
                )

            version_id = f"{design_id}_v{version_num}"
            conn.execute("""
                INSERT INTO design_versions (
                    version_id, design_id, version_number, user_prompt, device_type,
                    specification_json, cad_properties_json, validation_json,
                    material_candidates_json, export_paths_json, created_at_utc, app_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                version_id,
                design_id,
                version_num,
                user_prompt,
                device_type,
                json.dumps(specification),
                json.dumps(cad_properties),
                json.dumps(validation_report),
                json.dumps(material_candidates or []),
                json.dumps(export_paths or {}),
                now,
                f"{APP_NAME} {APP_VERSION}"
            ))

            conn.execute(
                "INSERT INTO audit_log (design_id, version_number, action, details, timestamp_utc) VALUES (?, ?, ?, ?, ?)",
                (design_id, version_num, "CREATE_VERSION", f"Saved version {version_num} for {device_type}", now)
            )
            conn.commit()

        return version_num

    def list_designs(self) -> list[dict]:
        with self._get_connection() as conn:
            cur = conn.execute("SELECT * FROM designs ORDER BY created_at_utc DESC")
            return [dict(r) for r in cur.fetchall()]

    def get_design(self, design_id: str) -> dict | None:
        with self._get_connection() as conn:
            cur = conn.execute("SELECT * FROM designs WHERE design_id = ?", (design_id,))
            row = cur.fetchone()
            if row:
                return dict(row)
            return None

    def get_design_history(self, design_id: str) -> list[dict]:
        with self._get_connection() as conn:
            cur = conn.execute(
                "SELECT * FROM design_versions WHERE design_id = ? ORDER BY version_number ASC",
                (design_id,)
            )
            return [dict(r) for r in cur.fetchall()]

    def get_latest_version(self, design_id: str) -> dict | None:
        with self._get_connection() as conn:
            cur = conn.execute(
                "SELECT * FROM design_versions WHERE design_id = ? ORDER BY version_number DESC LIMIT 1",
                (design_id,)
            )
            row = cur.fetchone()
            if row:
                return dict(row)
            return None
