"""SQLite storage for users and saved characters.

One file, created next to the app on first run. No server, no setup.
"""
import json
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "charcraft.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    username   TEXT    NOT NULL UNIQUE,
    salt       TEXT    NOT NULL,
    pw_hash    TEXT    NOT NULL,
    created_at TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS characters (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    name       TEXT    NOT NULL,
    data       TEXT    NOT NULL,
    created_at TEXT    NOT NULL,
    updated_at TEXT    NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with connect() as conn:
        conn.executescript(SCHEMA)


def _now():
    return datetime.now().isoformat(timespec="seconds")


# --- characters -----------------------------------------------------------

def list_characters(user_id):
    """Every character belonging to one designer, newest first."""
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, name, data, updated_at FROM characters "
            "WHERE user_id = ? ORDER BY updated_at DESC",
            (user_id,),
        ).fetchall()
    return [
        {
            "id": r["id"],
            "name": r["name"],
            "data": json.loads(r["data"]),
            "updated_at": r["updated_at"],
        }
        for r in rows
    ]


def get_character(char_id):
    with connect() as conn:
        r = conn.execute(
            "SELECT id, user_id, name, data FROM characters WHERE id = ?",
            (char_id,),
        ).fetchone()
    if r is None:
        return None
    return {"id": r["id"], "user_id": r["user_id"],
            "name": r["name"], "data": json.loads(r["data"])}


def create_character(user_id, name, data):
    stamp = _now()
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO characters (user_id, name, data, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, name, json.dumps(data), stamp, stamp),
        )
        return cur.lastrowid


def update_character(char_id, name, data):
    with connect() as conn:
        conn.execute(
            "UPDATE characters SET name = ?, data = ?, updated_at = ? WHERE id = ?",
            (name, json.dumps(data), _now(), char_id),
        )


def delete_character(char_id):
    with connect() as conn:
        conn.execute("DELETE FROM characters WHERE id = ?", (char_id,))
