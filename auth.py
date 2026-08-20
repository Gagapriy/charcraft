"""Account handling.

Passwords are never stored. Each account gets a random salt, and what goes
into the database is a PBKDF2-SHA256 derivation of salt + password. This is
worth two sentences in your report's implementation section.
"""
import hashlib
import hmac
import os
import sqlite3

from db import connect, _now

ITERATIONS = 200_000
MIN_PASSWORD_LENGTH = 6


class AuthError(Exception):
    """Raised when registration or sign-in cannot proceed."""


def _derive(password, salt_hex):
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), ITERATIONS
    )
    return dk.hex()


def register(username, password):
    """Create an account. Returns the new user id."""
    username = username.strip()
    if not username:
        raise AuthError("Enter a username.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise AuthError(
            f"Passwords need at least {MIN_PASSWORD_LENGTH} characters."
        )

    salt = os.urandom(16).hex()
    pw_hash = _derive(password, salt)
    try:
        with connect() as conn:
            cur = conn.execute(
                "INSERT INTO users (username, salt, pw_hash, created_at) "
                "VALUES (?, ?, ?, ?)",
                (username, salt, pw_hash, _now()),
            )
            return cur.lastrowid
    except sqlite3.IntegrityError:
        raise AuthError(f"The username '{username}' is taken. Pick another.")


def login(username, password):
    """Check credentials. Returns {'id', 'username'}."""
    with connect() as conn:
        row = conn.execute(
            "SELECT id, username, salt, pw_hash FROM users WHERE username = ?",
            (username.strip(),),
        ).fetchone()

    # Same message either way, so the form never reveals which usernames exist.
    if row is None or not hmac.compare_digest(
        _derive(password, row["salt"]), row["pw_hash"]
    ):
        raise AuthError("That username and password don't match.")

    return {"id": row["id"], "username": row["username"]}
