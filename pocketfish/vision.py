from dataclasses import dataclass
from typing import Any, Optional, Tuple
import cv2
import numpy as np
import chess

from .config import (
    LIGHT_SQUARE_BGR, DARK_SQUARE_BGR, COLOR_TOLERANCE, MIN_BOARD_SIZE,
    EMPTY, WHITE_PIECE, BLACK_PIECE,
)

@dataclass
class BoardLocation:
    monitor_index: int
    x: int
    y: int
    size: int

    @property
    def square_size(self) -> float:
        return self.size / 8.0

    def square_center(self, file: int, rank: int, flipped: bool) -> Tuple[int, int]:
        if flipped:
            col, row = 7 - file, rank
        else:
            col, row = file, 7 - rank
        cx = self.x + int((col + 0.5) * self.square_size)
        cy = self.y + int((row + 0.5) * self.square_size)
        return cx, cy


def _find_board_in_image(img_bgr: np.ndarray) -> Optional[Tuple[int, int, int]]:
    light = np.array(LIGHT_SQUARE_BGR, dtype=np.int16)
    dark = np.array(DARK_SQUARE_BGR, dtype=np.int16)

    diff_light = np.max(np.abs(img_bgr.astype(np.int16) - light), axis=2)
    diff_dark = np.max(np.abs(img_bgr.astype(np.int16) - dark), axis=2)
    mask = ((diff_light < COLOR_TOLERANCE) | (diff_dark < COLOR_TOLERANCE)).astype(np.uint8) * 255

    kernel = np.ones((9, 9), np.uint8)
    closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best, best_score = None, 0
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w < MIN_BOARD_SIZE or h < MIN_BOARD_SIZE:
            continue
        ratio = min(w, h) / max(w, h)
        if ratio < 0.9:
            continue
        fill = cv2.countNonZero(mask[y:y+h, x:x+w]) / float(w * h)
        if fill < 0.55:
            continue
        score = w * h * fill * ratio
        if score > best_score:
            best_score = score
            best = (x, y, min(w, h))
    return best


def find_board_on_any_monitor(sct: Any) -> Optional[BoardLocation]:
    for i, mon in enumerate(sct.monitors[1:], start=1):
        shot = np.array(sct.grab(mon))[:, :, :3]
        found = _find_board_in_image(shot)
        if found is not None:
            x, y, size = found
            return BoardLocation(
                monitor_index=i,
                x=mon["left"] + x,
                y=mon["top"] + y,
                size=size,
            )
    return None


def _square_is_light(sq_img: np.ndarray) -> bool:
    h, w = sq_img.shape[:2]
    s = max(2, min(h, w) // 20)
    corners = np.concatenate([
        sq_img[:s, :s].reshape(-1, 3),
        sq_img[:s, -s:].reshape(-1, 3),
        sq_img[-s:, :s].reshape(-1, 3),
        sq_img[-s:, -s:].reshape(-1, 3),
    ], axis=0)
    avg = np.median(corners, axis=0).astype(np.int16)
    light = np.array(LIGHT_SQUARE_BGR, dtype=np.int16)
    dark = np.array(DARK_SQUARE_BGR, dtype=np.int16)
    d_light = np.sum(np.abs(avg - light))
    d_dark = np.sum(np.abs(avg - dark))
    return d_light < d_dark


def classify_square(square_img: np.ndarray, is_light_square: bool) -> int:
    h, w = square_img.shape[:2]
    pad = int(min(h, w) * 0.15)
    center = square_img[pad:h-pad, pad:w-pad]
    if center.size == 0:
        return EMPTY

    gray = cv2.cvtColor(center, cv2.COLOR_BGR2GRAY)

    if is_light_square:
        white_mask = gray > 240
    else:
        white_mask = gray > 200

    black_mask = gray < 60

    white_frac = float(np.mean(white_mask))
    black_frac = float(np.mean(black_mask))

    THRESH = 0.03

    if white_frac < THRESH and black_frac < THRESH:
        return EMPTY
    if white_frac >= black_frac:
        return WHITE_PIECE
    return BLACK_PIECE


def board_to_grid(board_img: np.ndarray) -> np.ndarray:
    grid = np.zeros((8, 8), dtype=np.int8)
    h, w = board_img.shape[:2]
    sq_h, sq_w = h / 8.0, w / 8.0
    for r in range(8):
        for c in range(8):
            y0, y1 = int(r * sq_h), int((r + 1) * sq_h)
            x0, x1 = int(c * sq_w), int((c + 1) * sq_w)
            sq = board_img[y0:y1, x0:x1]
            is_light = _square_is_light(sq)
            grid[r, c] = classify_square(sq, is_light)
    return grid


def chess_to_grid(square: int, flipped: bool) -> Tuple[int, int]:
    file = chess.square_file(square)
    rank = chess.square_rank(square)
    if flipped:
        return rank, 7 - file
    return 7 - rank, file


def grid_from_board(board: chess.Board, flipped: bool) -> np.ndarray:
    grid = np.zeros((8, 8), dtype=np.int8)
    for sq, piece in board.piece_map().items():
        r, c = chess_to_grid(sq, flipped)
        grid[r, c] = WHITE_PIECE if piece.color == chess.WHITE else BLACK_PIECE
    return grid
