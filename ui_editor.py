"""The character editor.

Covers four of the six functional requirements: create by choosing size,
shape and colour; resize; recolour the whole character or a selected part;
and view the result in both 2D and 3D.

Every control writes into the same character dictionary and then asks for a
redraw, so the preview always reflects the current state. That immediate
feedback is "visibility of system status" — worth naming in the report.
"""
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox, QColorDialog, QComboBox, QDialog, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSlider, QTabWidget, QVBoxLayout, QWidget
)

import character
import render2d
import render3d
import theme


class EditorWindow(QDialog):
    def __init__(self, name, data, parent=None):
        super().__init__(parent)
        self.char = character.validate(data)
        self.selected_part = "body"
        self.three_d_stale = True

        self.setWindowTitle("Edit character")
        self.resize(980, 660)
        self.setStyleSheet(theme.STYLESHEET)
        self._build(name)
        self._refresh_part_labels()
        self.redraw()

    # --- layout ----------------------------------------------------------

    def _build(self, name):
        root = QHBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(18)

        panel = QFrame(objectName="Card")
        controls = QVBoxLayout(panel)
        controls.setContentsMargins(20, 20, 20, 20)
        controls.setSpacing(12)
        panel.setFixedWidth(320)

        controls.addWidget(QLabel("Name", objectName="Subtitle"))
        self.name_field = QLineEdit(name)
        controls.addWidget(self.name_field)

        controls.addWidget(QLabel("Type", objectName="Subtitle"))
        self.type_box = QComboBox()
        self.type_box.addItems([t.capitalize() for t in character.TYPES])
        self.type_box.setCurrentIndex(character.TYPES.index(self.char["type"]))
        self.type_box.currentIndexChanged.connect(self.change_type)
        controls.addWidget(self.type_box)

        self.scale_slider = self._slider(
            controls, "Overall size", character.SCALE_RANGE, self.char["scale"]
        )
        self.scale_slider.valueChanged.connect(self.change_scale)

        controls.addSpacing(6)
        controls.addWidget(QLabel("Proportions", objectName="Subtitle"))
        self.prop_sliders = {}
        for key in ("head", "body", "limbs"):
            slider = self._slider(controls, key.capitalize(),
                                  character.PROPORTION_RANGE,
                                  self.char["parts"][key])
            slider.valueChanged.connect(
                lambda value, k=key: self.change_proportion(k, value)
            )
            self.prop_sliders[key] = slider

        controls.addSpacing(6)
        controls.addWidget(QLabel("Colour", objectName="Subtitle"))
        self.part_box = QComboBox()
        self.part_box.currentIndexChanged.connect(self.change_part)
        controls.addWidget(self.part_box)

        self.whole_check = QCheckBox("Apply to the whole character")
        controls.addWidget(self.whole_check)

        self.colour_btn = QPushButton("Choose colour…")
        self.colour_btn.clicked.connect(self.pick_colour)
        controls.addWidget(self.colour_btn)

        controls.addStretch()

        buttons = QHBoxLayout()
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Save changes", objectName="Primary")
        save.clicked.connect(self.accept)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        controls.addLayout(buttons)

        root.addWidget(panel)

        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.tab_changed)

        self.fig2d = Figure(figsize=(5, 5), facecolor=theme.PAPER)
        self.canvas2d = FigureCanvas(self.fig2d)
        self.ax2d = self.fig2d.add_subplot(111)
        self.fig2d.subplots_adjust(0, 0, 1, 1)
        self.tabs.addTab(self._wrap(self.canvas2d), "2D view")

        self.fig3d = Figure(figsize=(5, 5), facecolor=theme.PAPER)
        self.canvas3d = FigureCanvas(self.fig3d)
        self.ax3d = self.fig3d.add_subplot(111, projection="3d")
        self.fig3d.subplots_adjust(0, 0, 1, 1)
        self.tabs.addTab(self._wrap(self.canvas3d), "3D view")

        root.addWidget(self.tabs, 1)

    def _wrap(self, canvas):
        holder = QWidget()
        box = QVBoxLayout(holder)
        box.setContentsMargins(0, 0, 0, 0)
        box.addWidget(canvas)
        return holder

    def _slider(self, layout, label_text, value_range, value):
        row = QHBoxLayout()
        label = QLabel(label_text, objectName="Subtitle")
        label.setFixedWidth(96)
        row.addWidget(label)
        slider = QSlider(Qt.Horizontal)
        slider.setRange(int(value_range[0] * 100), int(value_range[1] * 100))
        slider.setValue(int(value * 100))
        row.addWidget(slider)
        readout = QLabel(f"{value:.2f}×", objectName="Subtitle")
        readout.setFixedWidth(46)
        row.addWidget(readout)
        slider.valueChanged.connect(
            lambda v, lbl=readout: lbl.setText(f"{v / 100:.2f}×")
        )
        layout.addLayout(row)
        return slider

    def _refresh_part_labels(self):
        labels = character.PART_LABELS[self.char["type"]]
        self.part_box.blockSignals(True)
        self.part_box.clear()
        for key in character.PART_KEYS:
            self.part_box.addItem(labels[key], key)
        index = character.PART_KEYS.index(self.selected_part)
        self.part_box.setCurrentIndex(index)
        self.part_box.blockSignals(False)

    # --- control handlers ------------------------------------------------

    def change_type(self, index):
        self.char = character.switch_type(self.char, character.TYPES[index])
        self._refresh_part_labels()
        self.redraw()

    def change_scale(self, value):
        self.char["scale"] = value / 100
        self.redraw()

    def change_proportion(self, key, value):
        self.char["parts"][key] = value / 100
        self.redraw()

    def change_part(self, index):
        self.selected_part = self.part_box.itemData(index)
        self.redraw()

    def pick_colour(self):
        current = QColor(self.char["colors"][self.selected_part])
        chosen = QColorDialog.getColor(current, self, "Choose a colour")
        if chosen.isValid():
            character.set_colour(self.char, self.selected_part, chosen.name(),
                                 whole_character=self.whole_check.isChecked())
            self.redraw()

    # --- drawing ---------------------------------------------------------

    def tab_changed(self, index):
        if index == 1 and self.three_d_stale:
            self.draw_3d()

    def draw_3d(self):
        render3d.draw(self.ax3d, self.char)
        self.canvas3d.draw_idle()
        self.three_d_stale = False

    def redraw(self):
        render2d.draw(self.ax2d, self.char, self.selected_part)
        self.canvas2d.draw_idle()
        # 3D is slower, so it is only rebuilt when that tab is on screen.
        self.three_d_stale = True
        if self.tabs.currentIndex() == 1:
            self.draw_3d()

    # --- result ----------------------------------------------------------

    def result_data(self):
        return self.name_field.text().strip() or "Untitled", self.char
