"""Store: the User's data in a local SQLite database. Numbers only, never images."""
import json
import os
import sqlite3
import sys
from datetime import date
from pathlib import Path
from typing import Any

DAILY_STATS_COLUMNS = ("good_posture", "forward_lean", "side_lean", "mirror_count")


def default_path(platform: str = sys.platform) -> Path:
    """Per-user, and outside the install folder: %LOCALAPPDATA%\\Holdup on Windows, ~/Library/Application Support/Holdup
    on macOS, $XDG_DATA_HOME/holdup (~/.local/share/holdup) on Linux."""
    if platform == "win32":
        return Path(os.environ["LOCALAPPDATA"]) / "Holdup" / "holdup.db"
    if platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Holdup" / "holdup.db"
    return Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "holdup" / "holdup.db"


class Store:
    """Named values (the Baseline, settings) kept as JSON. Daily Stats can add their own table next to it."""

    def __init__(self, path: Path | str = ":memory:"):
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(path)
        with self._db:
            self._db.execute("CREATE TABLE IF NOT EXISTS setting (name TEXT PRIMARY KEY, value TEXT NOT NULL)")
            self._db.execute(
                "CREATE TABLE IF NOT EXISTS daily_stats (day TEXT PRIMARY KEY, good_posture REAL NOT NULL DEFAULT 0,"
                " forward_lean REAL NOT NULL DEFAULT 0, side_lean REAL NOT NULL DEFAULT 0,"
                " mirror_count INTEGER NOT NULL DEFAULT 0)"
            )

    def get(self, name: str, default: Any = None) -> Any:
        row = self._db.execute("SELECT value FROM setting WHERE name = ?", (name,)).fetchone()
        return json.loads(row[0]) if row else default

    def set(self, name: str, value: Any) -> None:
        with self._db:
            self._db.execute("REPLACE INTO setting (name, value) VALUES (?, ?)", (name, json.dumps(value)))

    def add_daily_stats(self, day: date, column: str, amount: float) -> None:
        """Add to one Daily Stats column (good_posture, forward_lean, side_lean or mirror_count) of a local date."""
        assert column in DAILY_STATS_COLUMNS
        with self._db:
            self._db.execute("INSERT OR IGNORE INTO daily_stats (day) VALUES (?)", (day.isoformat(),))
            self._db.execute(f"UPDATE daily_stats SET {column} = {column} + ? WHERE day = ?", (amount, day.isoformat()))

    def daily_stats(self, first: date, last: date) -> dict[date, tuple[float, float, float, int]]:
        """Days from first to last (inclusive) that have Daily Stats, as (good, forward, side, mirror_count)."""
        rows = self._db.execute(
            f"SELECT day, {', '.join(DAILY_STATS_COLUMNS)} FROM daily_stats WHERE day BETWEEN ? AND ?",
            (first.isoformat(), last.isoformat()),
        )
        return {date.fromisoformat(day): tuple(values) for day, *values in rows}

    def clear_daily_stats(self) -> None:
        """Delete every day's Daily Stats; the setting table (Baseline, settings) is untouched."""
        with self._db:
            self._db.execute("DELETE FROM daily_stats")

    def close(self) -> None:
        self._db.close()
