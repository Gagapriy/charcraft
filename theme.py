"""One place for every colour and control style in the app.

Keeping this in a single stylesheet is what makes the interface look
consistent, and consistency is one of the usability principles you will be
arguing for in the report. Change a value here and it changes everywhere.
"""

PLUM = "#2E2440"       # chrome and headers
PLUM_LIGHT = "#43354F"
PAPER = "#FBF7F0"      # work surface
BUTTER = "#F5C542"     # primary action
TEAL = "#3E7D74"       # secondary action
INK = "#1A1420"
MUTED = "#8A8095"
DANGER = "#C4553D"

STYLESHEET = f"""
QWidget {{
    background: {PLUM};
    color: {PAPER};
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 14px;
}}
QLabel#Title {{
    font-size: 26px;
    font-weight: 600;
    color: {PAPER};
}}
QLabel#Subtitle {{
    font-size: 13px;
    color: {MUTED};
}}
QLabel#Error {{
    color: {BUTTER};
    font-size: 13px;
}}
QFrame#Card {{
    background: {PLUM_LIGHT};
    border-radius: 14px;
}}
QLineEdit {{
    background: {PAPER};
    color: {INK};
    border: 2px solid transparent;
    border-radius: 8px;
    padding: 9px 11px;
    selection-background-color: {BUTTER};
    selection-color: {INK};
}}
QLineEdit:focus {{
    border: 2px solid {BUTTER};
}}
QPushButton {{
    background: {TEAL};
    color: {PAPER};
    border: none;
    border-radius: 8px;
    padding: 10px 18px;
    font-weight: 600;
}}
QPushButton:hover {{ background: #4A9086; }}
QPushButton:disabled {{ background: {PLUM_LIGHT}; color: {MUTED}; }}
QPushButton#Primary {{
    background: {BUTTER};
    color: {INK};
}}
QPushButton#Primary:hover {{ background: #FFD65C; }}
QPushButton#Danger {{ background: {DANGER}; }}
QPushButton#Danger:hover {{ background: #D3644C; }}
QPushButton#Link {{
    background: transparent;
    color: {BUTTER};
    padding: 4px;
    font-weight: 500;
    text-decoration: underline;
}}
QListWidget {{
    background: {PLUM_LIGHT};
    border: none;
    border-radius: 12px;
    padding: 6px;
    outline: none;
}}
QListWidget::item {{
    padding: 11px 12px;
    border-radius: 8px;
    color: {PAPER};
}}
QListWidget::item:selected {{
    background: {BUTTER};
    color: {INK};
    font-weight: 600;
}}
QComboBox {{
    background: {PAPER};
    color: {INK};
    border-radius: 8px;
    padding: 8px 11px;
}}
QComboBox QAbstractItemView {{
    background: {PAPER};
    color: {INK};
    selection-background-color: {BUTTER};
    selection-color: {INK};
}}
"""
