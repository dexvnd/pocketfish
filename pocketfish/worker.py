import time
from typing import List, Optional
import mss
import numpy as np
import chess
from PyQt5 import QtCore

from .config import (
    CAPTURE_INTERVAL,
    DEFAULT_DEPTH, DEFAULT_MOVETIME_MS,
    DEFAULT_THREADS, DEFAULT_HASH_MB, DEFAULT_SKILL,
)
from .engine import EngineWorker
from .moves import detect_orientation, resync_board
from .vision import (
    BoardLocation, board_to_grid, find_board_on_any_monitor,
)


class AssistantWorker(QtCore.QObject):
    statusChanged = QtCore.pyqtSignal(str, str)
    moveFound = QtCore.pyqtSignal(object, object)
    moveCleared = QtCore.pyqtSignal()
    boardRect = QtCore.pyqtSignal(object)
    debugInfo = QtCore.pyqtSignal(dict)
    moveLogged = QtCore.pyqtSignal(str)
    suggestionText = QtCore.pyqtSignal(str)

    def __init__(self, depth: int = DEFAULT_DEPTH,
                 movetime_ms: int = DEFAULT_MOVETIME_MS,
                 threads: int = DEFAULT_THREADS,
                 hash_mb: int = DEFAULT_HASH_MB,
                 skill: int = DEFAULT_SKILL):
        super().__init__()
        self.user_color = chess.WHITE
        self.show_debug = False
        self.suggestions_on = True
        self.recalibrate_requested = True
        self.reset_requested = False
        self.running = True
        self.awaiting_color_confirm = True
        self.engine = EngineWorker(
            depth=depth, movetime_ms=movetime_ms,
            threads=threads, hash_mb=hash_mb, skill=skill,
        )
        self._pending_opts = None
        self._last_score = None
        self._last_pv: List[str] = []

    def confirm_color(self, name: str):
        self.user_color = chess.WHITE if name == "White" else chess.BLACK
        self.awaiting_color_confirm = False
        self.reset_requested = True
        self.recalibrate_requested = True

    def set_color(self, name):
        self.user_color = chess.WHITE if name == "White" else chess.BLACK
        self.reset_requested = True
        self.recalibrate_requested = True

    def set_debug(self, on):
        self.show_debug = on

    def set_suggestions(self, on):
        self.suggestions_on = on
        if not on:
            self.moveCleared.emit()

    def set_engine_opts(self, d, mt, t, h, s):
        self._pending_opts = (d, mt, t, h, s)

    def stop(self):
        self.running = False

    def run(self):
        sct = mss.mss()
        board_loc: Optional[BoardLocation] = None
        flipped = False
        prev_grid: Optional[np.ndarray] = None
        chess_board = chess.Board()
        last_fps_ts = time.time()
        frames = 0
        fps = 0.0
        last_move_uci = ""
        unstable_count = 0
        last_suggest_fen: Optional[str] = None
        pending_fen: Optional[str] = None
        pending_count = 0
        PENDING_REQUIRED = 2

        def maybe_suggest(reason: str = ""):
            nonlocal last_suggest_fen
            if not self.suggestions_on:
                return
            if chess_board.turn != self.user_color:
                self.moveCleared.emit()
                self.suggestionText.emit("(opponent's turn)")
                last_suggest_fen = None
                return
            if chess_board.is_game_over():
                self.moveCleared.emit()
                return
            cur_fen = chess_board.fen()
            if cur_fen == last_suggest_fen:
                return
            self.suggestionText.emit("⌛ thinking...")
            self.moveCleared.emit()
            self._suggest(chess_board, board_loc, flipped)
            last_suggest_fen = cur_fen
            if reason:
                self.moveLogged.emit(f"  [suggest: {reason}]")

        while self.running:
            t0 = time.time()

            if self.awaiting_color_confirm:
                time.sleep(0.05)
                continue

            if self._pending_opts:
                self.engine.set_options(*self._pending_opts)
                self._pending_opts = None
                self.statusChanged.emit("Engine settings updated.", "good")

            if self.reset_requested:
                chess_board = chess.Board()
                prev_grid = None
                unstable_count = 0
                last_suggest_fen = None
                pending_fen = None
                pending_count = 0
                self.moveCleared.emit()
                self.reset_requested = False
                self.statusChanged.emit("Game state reset.", "good")

            if self.recalibrate_requested or board_loc is None:
                self.statusChanged.emit("Searching for chess board...", "warn")
                board_loc = find_board_on_any_monitor(sct)
                if board_loc is None:
                    self.boardRect.emit(None)
                    self._emit_debug_info(None, chess_board, fps, "no board",
                                          flipped=flipped)
                    time.sleep(0.5)
                    continue
                self.boardRect.emit((board_loc.x, board_loc.y, board_loc.size))
                flipped = (self.user_color == chess.BLACK)
                chess_board = chess.Board()
                prev_grid = None
                unstable_count = 0
                last_suggest_fen = None
                pending_fen = None
                pending_count = 0
                self.recalibrate_requested = False
                self.statusChanged.emit(
                    f"Board found on monitor {board_loc.monitor_index} ",
                    "good")

            region = {"left": board_loc.x, "top": board_loc.y,
                      "width": board_loc.size, "height": board_loc.size}
            try:
                shot = np.array(sct.grab(region))[:, :, :3]
            except Exception as e:
                self.statusChanged.emit(f"Capture error: {e}", "bad")
                self.recalibrate_requested = True
                time.sleep(0.5)
                continue

            curr_grid = board_to_grid(shot)
            frames += 1
            now = time.time()
            if now - last_fps_ts >= 1.0:
                fps = frames / (now - last_fps_ts)
                frames = 0
                last_fps_ts = now

            if prev_grid is None:
                prev_grid = curr_grid
                hint = (self.user_color == chess.BLACK)
                new_flipped, s_chosen, s_other = detect_orientation(
                    curr_grid, chess_board, hint)
                if new_flipped != flipped:
                    flipped = new_flipped
                    self.moveLogged.emit(
                        f"  [orient: {'flipped' if flipped else 'normal'} "
                        f"(score {s_chosen} vs {s_other})]")
                resynced = resync_board(curr_grid, flipped, chess_board)
                if resynced is not None:
                    chess_board = resynced
                maybe_suggest("init")
                self._emit_debug_info(board_loc, chess_board, fps, "init",
                                      curr_grid, last_move_uci, flipped=flipped)
                time.sleep(CAPTURE_INTERVAL)
                continue

            grid_stable = np.array_equal(prev_grid, curr_grid)
            prev_grid = curr_grid

            if not grid_stable:
                unstable_count += 1
                self._emit_debug_info(board_loc, chess_board, fps,
                                      f"changing({unstable_count})",
                                      curr_grid, last_move_uci, flipped=flipped)
                time.sleep(CAPTURE_INTERVAL)
                continue

            unstable_count = 0

            hint = flipped
            new_flipped, s_chosen, s_other = detect_orientation(
                curr_grid, chess_board, hint)
            if new_flipped != flipped:
                self.moveLogged.emit(
                    f"  [orient changed: {'flipped' if new_flipped else 'normal'} "
                    f"(score {s_chosen} vs {s_other})]")
                flipped = new_flipped
                last_suggest_fen = None

            resynced = resync_board(curr_grid, flipped, chess_board)
            advanced = False
            if resynced is not None and resynced.fen() != chess_board.fen():
                proposed_fen = resynced.fen()
                if proposed_fen == pending_fen:
                    pending_count += 1
                else:
                    pending_fen = proposed_fen
                    pending_count = 1

                if pending_count >= PENDING_REQUIRED:
                    diff = resynced.ply() - chess_board.ply()
                    if diff > 0 and resynced.move_stack:
                        last_move_uci = resynced.move_stack[-1].uci()
                        moved_by = "you" if resynced.turn != self.user_color else "opponent"
                        self.moveLogged.emit(
                            f"{moved_by}: {last_move_uci}"
                            + (f" (+{diff-1} more)" if diff > 1 else ""))
                        self.statusChanged.emit(
                            f"Move played by {moved_by}: {last_move_uci}", "status")
                    chess_board = resynced
                    pending_fen = None
                    pending_count = 0
                    advanced = True

                    if chess_board.is_game_over():
                        self.statusChanged.emit(
                            f"Game over: {chess_board.result()}", "good")
                        self.moveCleared.emit()
                        last_suggest_fen = None
                    else:
                        maybe_suggest("after move")
            else:
                pending_fen = None
                pending_count = 0

            if not advanced:
                maybe_suggest("stable")

            self._emit_debug_info(
                board_loc, chess_board, fps,
                "moved" if advanced
                else (f"pending({pending_count})" if pending_fen else "stable"),
                curr_grid, last_move_uci, flipped=flipped)
            time.sleep(max(0.0, CAPTURE_INTERVAL - (time.time() - t0)))

        self.engine.close()

    def _suggest(self, board, loc, flipped):
        move, score, pv = self.engine.analyse(board)
        self._last_score = score
        self._last_pv = [m.uci() for m in (pv or [])][:6]
        if move is None:
            self.moveCleared.emit()
            return
        sq = loc.square_size
        fx, fy = loc.square_center(chess.square_file(move.from_square),
                                   chess.square_rank(move.from_square), flipped)
        tx, ty = loc.square_center(chess.square_file(move.to_square),
                                   chess.square_rank(move.to_square), flipped)
        size = int(sq * 0.95)
        self.moveFound.emit(
            (int(fx - size/2), int(fy - size/2), size, size),
            (int(tx - size/2), int(ty - size/2), size, size),
        )
        try:
            san = board.san(move)
        except Exception:
            san = move.uci()
        self.suggestionText.emit(f"→ {san}")

    def _emit_debug_info(self, loc, board, fps, state, grid=None, last_move="",
                         flipped: bool = False):
        self.debugInfo.emit({
            "monitor": loc.monitor_index if loc else None,
            "pos": (loc.x, loc.y) if loc else None,
            "size": loc.size if loc else None,
            "turn": "White" if board.turn else "Black",
            "fps": fps,
            "fen": board.fen(),
            "state": state,
            "last_move": last_move,
            "score": self._last_score,
            "pv": self._last_pv,
            "grid": grid,
            "flipped": flipped,
        })
