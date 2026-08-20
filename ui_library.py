"""The character library: everything this designer has made, with a preview.

This is the app's home screen. The editor window opens from here (step 2).
"""
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QMessageBox, QPushButton, QVBoxLayout, QWidget
)

import character
import db
import render2d
import theme
from ui_editor import EditorWindow


class LibraryWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"CharCraft — {user['username']}")
        self.resize(940, 620)
        self._build()
        self.refresh()

    # --- layout ----------------------------------------------------------

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(26, 22, 26, 22)
        root.setSpacing(16)

        header = QHBoxLayout()
        heading = QLabel("Your characters", objectName="Title")
        header.addWidget(heading)
        header.addStretch()
        header.addWidget(QLabel("New:", objectName="Subtitle"))
        self.type_picker = QComboBox()
        self.type_picker.addItems([t.capitalize() for t in character.TYPES])
        self.type_picker.setFixedWidth(130)
        header.addWidget(self.type_picker)
        new_btn = QPushButton("Create character", objectName="Primary")
        new_btn.clicked.connect(self.create_character)
        header.addWidget(new_btn)
        root.addLayout(header)

        body = QHBoxLayout()
        body.setSpacing(18)

        left = QVBoxLayout()
        left.setSpacing(10)
        self.list = QListWidget()
        self.list.currentItemChanged.connect(lambda *_: self.update_preview())
        left.addWidget(self.list)

        actions = QHBoxLayout()
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.clicked.connect(self.edit_character)
        self.delete_btn = QPushButton("Delete", objectName="Danger")
        self.delete_btn.clicked.connect(self.delete_character)
        actions.addWidget(self.edit_btn)
        actions.addWidget(self.delete_btn)
        left.addLayout(actions)
        body.addLayout(left, 2)

        self.figure = Figure(figsize=(5, 5), facecolor=theme.PAPER)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(0, 0, 1, 1)
        body.addWidget(self.canvas, 3)

        root.addLayout(body)

        self.status = QLabel("", objectName="Subtitle")
        root.addWidget(self.status)

    # --- data ------------------------------------------------------------

    def refresh(self, select_id=None):
        self.list.clear()
        self.characters = db.list_characters(self.user["id"])
        for char in self.characters:
            item = QListWidgetItem(f"{char['name']}  ·  {char['data']['type']}")
            item.setData(Qt.UserRole, char["id"])
            self.list.addItem(item)

        if self.characters:
            target = 0
            if select_id is not None:
                target = next((i for i, c in enumerate(self.characters)
                               if c["id"] == select_id), 0)
            self.list.setCurrentRow(target)
            self.status.setText(f"{len(self.characters)} saved")
        else:
            self.status.setText(
                "No characters yet. Pick a type above and create your first one."
            )
        self.update_preview()

    def current(self):
        item = self.list.currentItem()
        if item is None:
            return None
        char_id = item.data(Qt.UserRole)
        return next((c for c in self.characters if c["id"] == char_id), None)

    def update_preview(self):
        char = self.current()
        has_selection = char is not None
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)

        self.ax.clear()
        if char is None:
            self.ax.set_facecolor(theme.PAPER)
            self.ax.axis("off")
        else:
            render2d.draw(self.ax, character.validate(char["data"]))
        self.canvas.draw_idle()

    # --- actions ---------------------------------------------------------

    def create_character(self):
        char_type = character.TYPES[self.type_picker.currentIndex()]
        existing = len([c for c in self.characters
                        if c["data"]["type"] == char_type])
        name = f"{char_type.capitalize()} {existing + 1}"
        blank = character.new_character(char_type)

        editor = EditorWindow(name, blank, self)
        if not editor.exec():
            return
        name, data = editor.result_data()
        new_id = db.create_character(self.user["id"], name, data)
        self.refresh(select_id=new_id)

    def edit_character(self):
        char = self.current()
        if char is None:
            return
        editor = EditorWindow(char["name"], char["data"], self)
        if editor.exec():
            name, data = editor.result_data()
            db.update_character(char["id"], name, data)
            self.refresh(select_id=char["id"])

    def delete_character(self):
        char = self.current()
        if char is None:
            return
        confirm = QMessageBox.question(
            self, "Delete character",
            f"Delete '{char['name']}'? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            db.delete_character(char["id"])
            self.refresh()
