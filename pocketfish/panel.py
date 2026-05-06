from PyQt5 import QtCore, QtGui, QtWidgets

from .config import (
    DEFAULT_DEPTH, DEFAULT_MOVETIME_MS, DEFAULT_SKILL,
    DEFAULT_THREADS, DEFAULT_HASH_MB, LOGO_PATH,
)
from .style import DARK_QSS
from .widgets import BoardView, EvalBar


class ControlPanel(QtWidgets.QWidget):
    colorChanged = QtCore.pyqtSignal(str)
    debugToggled = QtCore.pyqtSignal(bool)
    suggestionToggled = QtCore.pyqtSignal(bool)
    engineOptsChanged = QtCore.pyqtSignal(int, int, int, int, int)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PocketFish")
        self.setWindowIcon(QtGui.QIcon(LOGO_PATH))
        self.setStyleSheet(DARK_QSS)
        self.resize(360, 580)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)

        root = QtWidgets.QVBoxLayout(self)
        root.setSpacing(8)
        root.setContentsMargins(10, 10, 10, 10)

        title_row = QtWidgets.QHBoxLayout()
        logo = QtWidgets.QLabel()
        logo_pix = QtGui.QPixmap(LOGO_PATH).scaled(
            64, 64, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        logo.setPixmap(logo_pix)
        title_row.addWidget(logo)
        title_row.addStretch(1)
        self.suggestion_label = QtWidgets.QLabel("—")
        self.suggestion_label.setProperty("role", "big")
        title_row.addWidget(self.suggestion_label)
        root.addLayout(title_row)

        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self._build_main_tab(), "Main")
        tabs.addTab(self._build_debug_tab(), "Debug")
        root.addWidget(tabs, 1)

        self.status = QtWidgets.QLabel("starting...")
        self.status.setProperty("role", "status")
        self.status.setWordWrap(True)
        root.addWidget(self.status)

    def _build_main_tab(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)
        lay.setSpacing(6)
        lay.setContentsMargins(2, 8, 2, 2)

        top_row = QtWidgets.QHBoxLayout()
        side_lbl = QtWidgets.QLabel("Side:")
        side_lbl.setProperty("role", "muted")
        self.color_combo = QtWidgets.QComboBox()
        self.color_combo.addItems(["White", "Black"])
        self.color_combo.currentTextChanged.connect(self.colorChanged.emit)
        self.color_combo.setFixedWidth(80)
        top_row.addWidget(side_lbl)
        top_row.addWidget(self.color_combo)
        top_row.addSpacing(8)
        self.suggest_btn = QtWidgets.QPushButton("Suggestions ON")
        self.suggest_btn.setProperty("primary", True)
        self.suggest_btn.setCheckable(True)
        self.suggest_btn.setChecked(True)
        self.suggest_btn.toggled.connect(self._on_suggest_toggle)
        top_row.addWidget(self.suggest_btn, 1)
        lay.addLayout(top_row)

        view_row = QtWidgets.QHBoxLayout()
        view_row.setContentsMargins(0, 4, 0, 4)
        view_row.addStretch(1)
        self.board_view = BoardView()
        self.eval_bar = EvalBar()
        view_row.addWidget(self.board_view)
        view_row.addSpacing(6)
        view_row.addWidget(self.eval_bar)
        view_row.addStretch(1)
        lay.addLayout(view_row)

        eng_box = QtWidgets.QGroupBox("Stockfish")
        form = QtWidgets.QFormLayout(eng_box)
        form.setLabelAlignment(QtCore.Qt.AlignRight)
        form.setHorizontalSpacing(8)
        form.setVerticalSpacing(4)
        form.setContentsMargins(8, 6, 8, 4)

        self.depth_slider = self._mk_slider(1, 30, DEFAULT_DEPTH)
        self.depth_label = QtWidgets.QLabel(str(DEFAULT_DEPTH))
        self.depth_label.setProperty("role", "metric")
        form.addRow("Depth", self._wrap_slider(self.depth_slider, self.depth_label))

        self.movetime_slider = self._mk_slider(50, 3000, DEFAULT_MOVETIME_MS)
        self.movetime_label = QtWidgets.QLabel(f"{DEFAULT_MOVETIME_MS}ms")
        self.movetime_label.setProperty("role", "metric")
        form.addRow("Time", self._wrap_slider(self.movetime_slider, self.movetime_label, "ms"))

        self.skill_slider = self._mk_slider(0, 20, DEFAULT_SKILL)
        self.skill_label = QtWidgets.QLabel(str(DEFAULT_SKILL))
        self.skill_label.setProperty("role", "metric")
        form.addRow("Skill", self._wrap_slider(self.skill_slider, self.skill_label))

        cpu_row = QtWidgets.QHBoxLayout()
        cpu_row.setContentsMargins(0, 0, 0, 0)
        self.threads_spin = QtWidgets.QSpinBox()
        self.threads_spin.setRange(1, 16)
        self.threads_spin.setValue(DEFAULT_THREADS)
        self.threads_spin.setFixedWidth(60)
        self.hash_spin = QtWidgets.QSpinBox()
        self.hash_spin.setRange(16, 4096)
        self.hash_spin.setSingleStep(16)
        self.hash_spin.setValue(DEFAULT_HASH_MB)
        self.hash_spin.setSuffix(" MB")
        self.hash_spin.setFixedWidth(90)
        threads_lbl = QtWidgets.QLabel("Threads")
        threads_lbl.setProperty("role", "muted")
        hash_lbl = QtWidgets.QLabel("  Hash")
        hash_lbl.setProperty("role", "muted")
        cpu_row.addWidget(threads_lbl)
        cpu_row.addWidget(self.threads_spin)
        cpu_row.addWidget(hash_lbl)
        cpu_row.addWidget(self.hash_spin)
        cpu_row.addStretch(1)
        cpu_w = QtWidgets.QWidget()
        cpu_w.setLayout(cpu_row)
        form.addRow("", cpu_w)

        apply_btn = QtWidgets.QPushButton("Apply")
        apply_btn.clicked.connect(self._emit_engine_opts)
        form.addRow("", apply_btn)

        lay.addWidget(eng_box)

        for s, lbl, suf in [
            (self.depth_slider, self.depth_label, ""),
            (self.movetime_slider, self.movetime_label, "ms"),
            (self.skill_slider, self.skill_label, ""),
        ]:
            s.valueChanged.connect(lambda v, l=lbl, x=suf: l.setText(f"{v}{x}"))

        lay.addStretch(1)
        return w

    def _build_debug_tab(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(w)
        lay.setSpacing(6)
        lay.setContentsMargins(2, 8, 2, 2)

        self.debug_btn = QtWidgets.QPushButton("Screen Overlay")
        self.debug_btn.setCheckable(True)
        self.debug_btn.toggled.connect(self._on_debug_toggle)
        lay.addWidget(self.debug_btn)

        info_box = QtWidgets.QGroupBox("Detection")
        grid = QtWidgets.QGridLayout(info_box)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(2)
        grid.setContentsMargins(8, 6, 8, 6)

        def _muted(t: str) -> QtWidgets.QLabel:
            l = QtWidgets.QLabel(t)
            l.setProperty("role", "muted")
            return l

        def _metric() -> QtWidgets.QLabel:
            l = QtWidgets.QLabel("—")
            l.setProperty("role", "metric")
            return l

        self.lbl_monitor = _metric()
        self.lbl_pos = _metric()
        self.lbl_size = _metric()
        self.lbl_turn = _metric()
        self.lbl_fps = _metric()
        self.lbl_eval = _metric()
        self.lbl_state = _metric()
        self.lbl_orient = _metric()

        grid.addWidget(_muted("Monitor"), 0, 0)
        grid.addWidget(self.lbl_monitor, 0, 1)
        grid.addWidget(_muted("Position"), 1, 0)
        grid.addWidget(self.lbl_pos, 1, 1)
        grid.addWidget(_muted("Size"), 2, 0)
        grid.addWidget(self.lbl_size, 2, 1)
        grid.addWidget(_muted("Turn"), 0, 2)
        grid.addWidget(self.lbl_turn, 0, 3)
        grid.addWidget(_muted("FPS"), 1, 2)
        grid.addWidget(self.lbl_fps, 1, 3)
        grid.addWidget(_muted("Eval"), 2, 2)
        grid.addWidget(self.lbl_eval, 2, 3)
        grid.addWidget(_muted("State"), 3, 0)
        grid.addWidget(self.lbl_state, 3, 1)
        grid.addWidget(_muted("Orient"), 3, 2)
        grid.addWidget(self.lbl_orient, 3, 3)
        lay.addWidget(info_box)

        pv_box = QtWidgets.QGroupBox("Position")
        pv = QtWidgets.QVBoxLayout(pv_box)
        pv.setSpacing(4)
        pv.setContentsMargins(8, 6, 8, 6)
        self.fen_edit = QtWidgets.QLineEdit()
        self.fen_edit.setReadOnly(True)
        self.fen_edit.setPlaceholderText("FEN...")
        self.pv_label = QtWidgets.QLabel("PV: —")
        self.pv_label.setProperty("role", "metric")
        self.pv_label.setWordWrap(True)
        pv.addWidget(self.fen_edit)
        pv.addWidget(self.pv_label)
        lay.addWidget(pv_box)

        log_box = QtWidgets.QGroupBox("Move Log")
        lb = QtWidgets.QVBoxLayout(log_box)
        lb.setContentsMargins(8, 6, 8, 6)
        self.move_log = QtWidgets.QPlainTextEdit()
        self.move_log.setReadOnly(True)
        lb.addWidget(self.move_log)
        lay.addWidget(log_box, 1)

        return w

    def _mk_slider(self, lo: int, hi: int, val: int) -> QtWidgets.QSlider:
        s = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        s.setRange(lo, hi)
        s.setValue(val)
        return s

    def _wrap_slider(self, slider: QtWidgets.QSlider, label: QtWidgets.QLabel, suffix: str = "") -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        h = QtWidgets.QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        h.addWidget(slider, 1)
        label.setMinimumWidth(60)
        label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        h.addWidget(label)
        return w

    def _on_debug_toggle(self, on: bool) -> None:
        self.debug_btn.setText("Screen Overlay ON" if on else "Screen Overlay")
        self.debugToggled.emit(on)

    def _on_suggest_toggle(self, on: bool) -> None:
        self.suggest_btn.setText("Suggestions ON" if on else "Suggestions OFF")
        self.suggestionToggled.emit(on)

    def _emit_engine_opts(self) -> None:
        self.engineOptsChanged.emit(
            self.depth_slider.value(), self.movetime_slider.value(),
            self.threads_spin.value(), self.hash_spin.value(),
            self.skill_slider.value(),
        )

    def set_status(self, text: str, kind: str = "status") -> None:
        self.status.setText(text)
        role = {"good": "statusGood", "warn": "statusWarn",
                "bad": "statusBad"}.get(kind, "status")
        self.status.setProperty("role", role)
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)

    def set_suggestion(self, text: str) -> None:
        self.suggestion_label.setText(text)

    def append_log(self, line: str) -> None:
        self.move_log.appendPlainText(line)

    def apply_engine_settings(self, depth: int, movetime_ms: int,
                              threads: int, hash_mb: int, skill: int) -> None:
        self.depth_slider.setValue(depth)
        self.depth_label.setText(str(depth))
        self.movetime_slider.setValue(movetime_ms)
        self.movetime_label.setText(f"{movetime_ms}ms")
        self.skill_slider.setValue(skill)
        self.skill_label.setText(str(skill))
        self.threads_spin.setValue(threads)
        self.hash_spin.setValue(hash_mb)
