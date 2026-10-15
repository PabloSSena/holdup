"""Store: the User's data in a local SQLite database. Numbers only, never images."""
import json
import os
import sqlite3
from pathlib import Path
from typing import Any


def default_path() -> Path:
    """%LOCALAPPDATA%\\Holdup\\holdup.db: per-user, and outside the install folder."""
    return Path(os.environ["LOCALAPPDATA"]) / "Holdup" / "holdup.db"


class Store:
    """Named values (the Baseline, settings) kept as JSON. Daily Stats can add their own table next to it."""

    def __init__(self, path: Path | str = ":memory:"):
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(path)
        with self._db:
            self._db.execute("CREATE TABLE IF NOT EXISTS setting (name TEXT PRIMARY KEY, value TEXT NOT NULL)")

    def get(self, name: str, default: Any = None) -> Any:
        row = self._db.execute("SELECT value FROM setting WHERE name = ?", (name,)).fetchone()
        return json.loads(row[0]) if row else default

    def set(self, name: str, value: Any) -> None:
        with self._db:
            self._db.execute("REPLACE INTO setting (name, value) VALUES (?, ?)", (name, json.dumps(value)))

    def close(self) -> None:
        self._db.close()
