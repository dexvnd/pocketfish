from typing import Optional

from PyQt5 import QtCore, QtGui, QtWidgets

from .config import (
    DEFAULT_DEPTH, DEFAULT_MOVETIME_MS, DEFAULT_SKILL,
    DEFAULT_THREADS, DEFAULT_HASH_MB, LOGO_PATH,
)
from .style import DARK_QSS


class StartupDialog(QtWidgets.QDialog):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("PocketFish — Setup")
        self.setWindowIcon(QtGui.QIcon(LOGO_PATH))
        self.setStyleSheet(DARK_QSS)
        self.setModal(True)
        self.setFixedSize(440, 560)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)

        self.choice: Optional[str] = None
        self.depth: int = DEFAULT_DEPTH
        self.movetime_ms: int = DEFAULT_MOVETIME_MS
        self.skill: int = DEFAULT_SKILL
        self.threads: int = DEFAULT_THREADS
        self.hash_mb: int = DEFAULT_HASH_MB

        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(12)

        header_row = QtWidgets.QHBoxLayout()
        header_row.addStretch(1)
        logo = QtWidgets.QLabel()
        logo_pix = QtGui.QPixmap(LOGO_PATH).scaled(
            48, 48, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        logo.setPixmap(logo_pix)
        header_row.addWidget(logo)
        title = QtWidgets.QLabel("PocketFish")
        title.setProperty("role", "header")
        header_row.addWidget(title)
        header_row.addStretch(1)
        lay.addLayout(header_row)

        sub = QtWidgets.QLabel(
            "Pick your side and configure Stockfish. These engine "
            "settings will be applied at startup."
        )
        sub.setProperty("role", "muted")
        sub.setAlignment(QtCore.Qt.AlignCenter)
        sub.setWordWrap(True)
        lay.addWidget(sub)

        side_box = QtWidgets.QGroupBox("Your side")
        side_lay = QtWidgets.QHBoxLayout(side_box)
        side_lay.setSpacing(10)
        side_lay.setContentsMargins(10, 14, 10, 10)

        self.side_group = QtWidgets.QButtonGroup(self)
        self.side_group.setExclusive(True)

        self.white_btn = QtWidgets.QPushButton("♔  White")
        self.white_btn.setProperty("side", True)
        self.white_btn.setCheckable(True)
        self.white_btn.setChecked(True)
        self.side_group.addButton(self.white_btn)
        side_lay.addWidget(self.white_btn)

        self.black_btn = QtWidgets.QPushButton("♚  Black")
        self.black_btn.setProperty("side", True)
        self.black_btn.setCheckable(True)
        self.side_group.addButton(self.black_btn)
        side_lay.addWidget(self.black_btn)

        lay.addWidget(side_box)

        eng_box = QtWidgets.QGroupBox("Stockfish settings")
        form = QtWidgets.QFormLayout(eng_box)
        form.setLabelAlignment(QtCore.Qt.AlignRight)
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        form.setContentsMargins(12, 14, 12, 10)

        self.depth_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.depth_slider.setRange(1, 30)
        self.depth_slider.setValue(DEFAULT_DEPTH)
        self.depth_label = QtWidgets.QLabel(str(DEFAULT_DEPTH))
        self.depth_label.setProperty("role", "metric")
        self.depth_label.setMinimumWidth(60)
        self.depth_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.depth_slider.valueChanged.connect(
            lambda v: self.depth_label.setText(str(v)))
        form.addRow("Depth", self._wrap(self.depth_slider, self.depth_label))

        self.movetime_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.movetime_slider.setRange(50, 3000)
        self.movetime_slider.setValue(DEFAULT_MOVETIME_MS)
        self.movetime_label = QtWidgets.QLabel(f"{DEFAULT_MOVETIME_MS}ms")
        self.movetime_label.setProperty("role", "metric")
        self.movetime_label.setMinimumWidth(60)
        self.movetime_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.movetime_slider.valueChanged.connect(
            lambda v: self.movetime_label.setText(f"{v}ms"))
        form.addRow("Time", self._wrap(self.movetime_slider, self.movetime_label))

        self.skill_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.skill_slider.setRange(0, 20)
        self.skill_slider.setValue(DEFAULT_SKILL)
        self.skill_label = QtWidgets.QLabel(str(DEFAULT_SKILL))
        self.skill_label.setProperty("role", "metric")
        self.skill_label.setMinimumWidth(60)
        self.skill_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.skill_slider.valueChanged.connect(
            lambda v: self.skill_label.setText(str(v)))
        form.addRow("Skill", self._wrap(self.skill_slider, self.skill_label))

        cpu_row = QtWidgets.QHBoxLayout()
        cpu_row.setContentsMargins(0, 0, 0, 0)
        self.threads_spin = QtWidgets.QSpinBox()
        self.threads_spin.setRange(1, 16)
        self.threads_spin.setValue(DEFAULT_THREADS)
        self.threads_spin.setFixedWidth(70)
        self.hash_spin = QtWidgets.QSpinBox()
        self.hash_spin.setRange(16, 4096)
        self.hash_spin.setSingleStep(16)
        self.hash_spin.setValue(DEFAULT_HASH_MB)
        self.hash_spin.setSuffix(" MB")
        self.hash_spin.setFixedWidth(100)
        threads_lbl = QtWidgets.QLabel("Threads")
        threads_lbl.setProperty("role", "muted")
        hash_lbl = QtWidgets.QLabel("  Hash")
        hash_lbl.setProperty("role", "muted")
        cpu_row.addWidget(threads_lbl)
        cpu_row.addWidget(self.threads_spin)
        cpu_row.addSpacing(8)
        cpu_row.addWidget(hash_lbl)
        cpu_row.addWidget(self.hash_spin)
        cpu_row.addStretch(1)
        cpu_w = QtWidgets.QWidget()
        cpu_w.setLayout(cpu_row)
        form.addRow("CPU", cpu_w)

        lay.addWidget(eng_box)

        preset_row = QtWidgets.QHBoxLayout()
        preset_lbl = QtWidgets.QLabel("Strength:")
        preset_lbl.setProperty("role", "muted")
        preset_row.addWidget(preset_lbl)
        for name, vals, tip in [
            ("Beginner", ( 6,  150,  2, 1,  64), "~1200 Elo · 65–72% accuracy\nMore human"),
            ("Casual",   (10,  200,  6, 1,  64), "~1550 Elo · 75–82% accuracy\nMakes some mistakes, hard to detect"),
            ("Club",     (14,  300, 10, 2, 128), "~1850 Elo · 82–87% accuracy\nBest for online play"),
            ("Strong",   (18,  500, 14, 2, 256), "~2150 Elo · 87–92% accuracy\nGetting borderline for anti cheat"),
            ("Master",   (22, 1000, 20, 4, 512), "~2850 Elo · 95%+ accuracy\nAlmost perfect play, will likely flag anti cheat"),
        ]:
            b = QtWidgets.QPushButton(name)
            b.setToolTip(tip)
            b.clicked.connect(lambda _=False, v=vals: self._apply_preset(*v))
            preset_row.addWidget(b)
        preset_row.addStretch(1)
        lay.addLayout(preset_row)

        accuracy_hint = QtWidgets.QLabel(
            "Lower strength = more human which wont flag chess.com anticheat\n"
            "Master plays almost perfectly and may flag anticheat"
        )
        accuracy_hint.setProperty("role", "muted")
        accuracy_hint.setWordWrap(True)
        accuracy_hint.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(accuracy_hint)

        lay.addStretch(1)

        self.start_btn = QtWidgets.QPushButton("Start")
        self.start_btn.setProperty("primary", True)
        self.start_btn.setMinimumHeight(44)
        self.start_btn.clicked.connect(self._on_start)
        lay.addWidget(self.start_btn)

        hint = QtWidgets.QLabel(
            "You can tweak these later from the Main tab (Apply button)."
        )
        hint.setProperty("role", "muted")
        hint.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(hint)

    @staticmethod
    def _wrap(slider: QtWidgets.QSlider, label: QtWidgets.QLabel) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        h = QtWidgets.QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        h.addWidget(slider, 1)
        h.addWidget(label)
        return w

    def _apply_preset(self, depth: int, movetime_ms: int, skill: int, threads: int, hash_mb: int) -> None:
        self.depth_slider.setValue(depth)
        self.movetime_slider.setValue(movetime_ms)
        self.skill_slider.setValue(skill)
        self.threads_spin.setValue(threads)
        self.hash_spin.setValue(hash_mb)

    def _on_start(self) -> None:
        self.choice = "White" if self.white_btn.isChecked() else "Black"
        self.depth = self.depth_slider.value()
        self.movetime_ms = self.movetime_slider.value()
        self.skill = self.skill_slider.value()
        self.threads = self.threads_spin.value()
        self.hash_mb = self.hash_spin.value()
        self.accept()

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        super().showEvent(event)
        screen = QtWidgets.QApplication.primaryScreen()
        if screen is not None:
            geo = screen.availableGeometry()
            self.move(geo.center().x() - self.width() // 2,
                      geo.center().y() - self.height() // 2)
        self.raise_()
        self.activateWindow()
