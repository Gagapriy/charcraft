"""CharCraft — character designer for educational games.

Run with:  python main.py
"""
import sys

import matplotlib
matplotlib.use("QtAgg")          # must be set before pyplot is touched

from PySide6.QtWidgets import QApplication

import db
import theme
from ui_library import LibraryWindow
from ui_login import LoginWindow


class App:
    def __init__(self):
        self.login = LoginWindow()
        self.login.signed_in.connect(self.open_library)
        self.library = None

    def start(self):
        self.login.show()

    def open_library(self, user):
        self.library = LibraryWindow(user)
        self.library.show()
        self.login.close()


def main():
    db.init_db()
    qt = QApplication(sys.argv)
    qt.setStyleSheet(theme.STYLESHEET)
    app = App()
    app.start()
    sys.exit(qt.exec())


if __name__ == "__main__":
    main()
