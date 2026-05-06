import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from .config import EMPTY, WHITE_PIECE

class BoardView(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(192, 192)
        self.grid = np.zeros((8, 8), dtype=np.int8)

    def set_grid(self, grid):
        self.grid = grid.copy()
        self.update()

    def paintEvent(self, _):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)
        sq = self.width() / 8.0
        for r in range(8):
            for c in range(8):
                x, y = int(c * sq), int(r * sq)
                light = (r + c) % 2 == 0
                color = QtGui.QColor(238, 223, 181) if light else QtGui.QColor(118, 150, 88)
                p.fillRect(x, y, int(sq) + 1, int(sq) + 1, color)
                v = self.grid[r, c]
                if v != EMPTY:
                    cx, cy = x + sq/2, y + sq/2
                    radius = sq * 0.32
                    if v == WHITE_PIECE:
                        p.setBrush(QtGui.QColor(245, 245, 245))
                        p.setPen(QtGui.QPen(QtGui.QColor(20, 20, 20), 1.5))
                    else:
                        p.setBrush(QtGui.QColor(25, 25, 25))
                        p.setPen(QtGui.QPen(QtGui.QColor(220, 220, 220), 1.5))
                    p.drawEllipse(QtCore.QPointF(cx, cy), radius, radius)
        p.end()

class EvalBar(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(22, 192)
        self.cp = 0
        self.mate = None

    def set_eval(self, score):
        if score is None:
            self.cp, self.mate = 0, None
        else:
            w = score.white()
            if w.is_mate():
                self.mate = w.mate()
                self.cp = 0
            else:
                self.mate = None
                self.cp = w.score(mate_score=10000) or 0
        self.update()

    def paintEvent(self, _):
        p = QtGui.QPainter(self)
        p.fillRect(self.rect(), QtGui.QColor(40, 40, 40))
        if self.mate is not None:
            frac = 1.0 if self.mate > 0 else 0.0
        else:
            frac = 1 / (1 + np.exp(-self.cp / 400.0))
        h = self.height()
        white_h = int(h * frac)
        p.fillRect(0, h - white_h, self.width(), white_h, QtGui.QColor(245, 245, 245))
        p.setPen(QtGui.QPen(QtGui.QColor(180, 180, 180), 1, QtCore.Qt.DashLine))
        p.drawLine(0, h // 2, self.width(), h // 2)
        label = f"M{abs(self.mate)}" if self.mate is not None else f"{self.cp/100:+.1f}"
        p.setPen(QtGui.QColor(0, 0, 0) if frac > 0.5 else QtGui.QColor(255, 255, 255))
        p.setFont(QtGui.QFont("Segoe UI", 8, QtGui.QFont.Bold))
        align = QtCore.Qt.AlignHCenter | (QtCore.Qt.AlignBottom if frac > 0.5 else QtCore.Qt.AlignTop)
        p.drawText(self.rect(), align, label)
        p.end()
