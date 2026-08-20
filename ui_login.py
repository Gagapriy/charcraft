"""Sign-in and registration.

One window with two modes rather than two windows, so a designer who picks
the wrong one does not lose what they typed.
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
)

import auth


class LoginWindow(QWidget):
    signed_in = Signal(dict)   # emits {'id': ..., 'username': ...}

    def __init__(self):
        super().__init__()
        self.registering = False
        self.setWindowTitle("CharCraft")
        self.setFixedSize(420, 460)
        self._build()
        self._apply_mode()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(34, 34, 34, 34)

        card = QFrame(objectName="Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 30, 28, 30)
        layout.setSpacing(12)

        self.title = QLabel("Welcome back", objectName="Title")
        self.subtitle = QLabel(objectName="Subtitle")
        self.subtitle.setWordWrap(True)
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        layout.addSpacing(10)

        self.username = QLineEdit(placeholderText="Username")
        self.password = QLineEdit(placeholderText="Password")
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.username)
        layout.addWidget(self.password)

        self.confirm = QLineEdit(placeholderText="Confirm password")
        self.confirm.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm)

        self.error = QLabel("", objectName="Error")
        self.error.setWordWrap(True)
        layout.addWidget(self.error)

        self.submit = QPushButton(objectName="Primary")
        self.submit.clicked.connect(self._submit)
        layout.addWidget(self.submit)

        self.toggle = QPushButton(objectName="Link", cursor=Qt.PointingHandCursor)
        self.toggle.clicked.connect(self._toggle_mode)
        layout.addWidget(self.toggle, alignment=Qt.AlignHCenter)

        layout.addStretch()
        outer.addWidget(card)

        for field in (self.username, self.password, self.confirm):
            field.returnPressed.connect(self._submit)

    def _apply_mode(self):
        if self.registering:
            self.title.setText("Create an account")
            self.subtitle.setText("Your characters are saved to your account.")
            self.submit.setText("Create account")
            self.toggle.setText("I already have an account")
            self.confirm.show()
        else:
            self.title.setText("Welcome back")
            self.subtitle.setText("Sign in to open your character library.")
            self.submit.setText("Sign in")
            self.toggle.setText("Create an account")
            self.confirm.hide()
        self.error.setText("")

    def _toggle_mode(self):
        self.registering = not self.registering
        self._apply_mode()

    def _submit(self):
        name = self.username.text()
        pw = self.password.text()
        try:
            if self.registering:
                if pw != self.confirm.text():
                    raise auth.AuthError("The two passwords don't match.")
                auth.register(name, pw)
                user = auth.login(name, pw)
            else:
                user = auth.login(name, pw)
        except auth.AuthError as exc:
            self.error.setText(str(exc))
            return
        self.signed_in.emit(user)
