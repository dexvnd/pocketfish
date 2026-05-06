import math
from typing import Optional, Tuple
from PyQt5 import QtCore, QtGui, QtWidgets

Box = Tuple[int, int, int, int]
BoardRect = Tuple[int, int, int]


class Overlay(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.Tool
            | QtCore.Qt.WindowTransparentForInput
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        screens = QtWidgets.QApplication.screens()
        self.setGeometry(screens[0].virtualGeometry())

        self.from_box: Optional[Box] = None
        self.to_box: Optional[Box] = None
        self.board_rect: Optional[BoardRect] = None
        self.show_debug_outline: bool = False

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def set_move(self, fb: Box, tb: Box) -> None:
        self.from_box, self.to_box = fb, tb

    def clear_move(self) -> None:
        self.from_box = self.to_box = None

    def set_board_rect(self, r: Optional[BoardRect]) -> None:
        self.board_rect = r

    def set_debug(self, on: bool) -> None:
        self.show_debug_outline = on

    def paintEvent(self, _: QtGui.QPaintEvent) -> None:
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)
        geom = self.geometry()
        p.translate(-geom.x(), -geom.y())

        if self.from_box is not None:
            self._draw_box(p, *self.from_box, QtGui.QColor(255, 200, 0, 220))
        if self.to_box is not None:
            self._draw_box(p, *self.to_box, QtGui.QColor(50, 230, 80, 230))
            if self.from_box is not None:
                self._draw_arrow(p, self.from_box, self.to_box)

        if self.show_debug_outline and self.board_rect is not None:
            bx, by, bsz = self.board_rect
            pen = QtGui.QPen(QtGui.QColor(255, 0, 255, 220), 2)
            p.setPen(pen)
            p.setBrush(QtCore.Qt.NoBrush)
            p.drawRect(bx, by, bsz, bsz)
            step = bsz / 8.0
            pen.setColor(QtGui.QColor(255, 0, 255, 90))
            p.setPen(pen)
            for i in range(1, 8):
                p.drawLine(int(bx + i*step), by, int(bx + i*step), by + bsz)
                p.drawLine(bx, int(by + i*step), bx + bsz, int(by + i*step))
        p.end()

    @staticmethod
    def _draw_box(p: QtGui.QPainter, x: int, y: int, w: int, h: int, color: QtGui.QColor) -> None:
        p.setPen(QtGui.QPen(color, 5))
        p.setBrush(QtCore.Qt.NoBrush)
        p.drawRoundedRect(x, y, w, h, 6, 6)

    @staticmethod
    def _draw_arrow(p: QtGui.QPainter, fb: Box, tb: Box) -> None:
        fx = fb[0] + fb[2] / 2
        fy = fb[1] + fb[3] / 2
        tx = tb[0] + tb[2] / 2
        ty = tb[1] + tb[3] / 2
        pen = QtGui.QPen(QtGui.QColor(50, 230, 80, 230), 7)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        p.setPen(pen)
        p.drawLine(int(fx), int(fy), int(tx), int(ty))
        angle = math.atan2(ty - fy, tx - fx)
        for off in (math.pi - 0.5, math.pi + 0.5):
            hx = tx + 26 * math.cos(angle + off)
            hy = ty + 26 * math.sin(angle + off)
            p.drawLine(int(tx), int(ty), int(hx), int(hy))
