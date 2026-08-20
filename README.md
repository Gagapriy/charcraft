# CharCraft

Desktop application for designing simple cartoon characters for educational
games. Built for PUSL3122 (HCI, Computer Graphics and Visualisation).

A character is stored as a small set of parameters — type, scale, part
proportions and colours — and both the 2D and 3D views are rendered from
that same model.

## Running it

    python -m venv .venv
    source .venv/bin/activate        # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    python main.py

A `charcraft.db` SQLite file is created next to the app on first run.

## Files

| File | What it does |
|---|---|
| `main.py` | Entry point; wires sign-in to the library |
| `db.py` | SQLite schema and character CRUD |
| `auth.py` | Registration and sign-in (PBKDF2-hashed passwords) |
| `character.py` | The character parameter model |
| `render2d.py` | Draws a character in 2D from its parameters |
| `theme.py` | Colours and control styling |
| `ui_login.py` | Sign-in / registration window |
| `ui_library.py` | Character library with live preview |
