import os
import sys
import shutil
from typing import List, Optional, Tuple
from dexvstuff import Logger
import chess
import chess.engine
from PyQt5 import QtWidgets

from .config import (
    PROJECT_ROOT, STOCKFISH_PATH, DEFAULT_DEPTH, DEFAULT_MOVETIME_MS,
    DEFAULT_THREADS, DEFAULT_HASH_MB, DEFAULT_SKILL,
)

log = Logger("PocketFish")

def resolve_stockfish_path(path: str) -> Optional[str]:
    if path:
        if os.path.isfile(path):
            return os.path.abspath(path)
        found = shutil.which(path)
        if found:
            return found

    here = PROJECT_ROOT
    candidates = []
    for root in (here, os.path.join(here, "stockfish")):
        if not os.path.isdir(root):
            continue
        for name in os.listdir(root):
            low = name.lower()
            if low.startswith("stockfish") and (low.endswith(".exe") or "." not in low):
                candidates.append(os.path.join(root, name))
    if candidates:
        return candidates[0]

    for n in ("stockfish", "stockfish.exe"):
        found = shutil.which(n)
        if found:
            return found
    return None


class EngineWorker:
    def __init__(self, path: str = STOCKFISH_PATH, depth: int = DEFAULT_DEPTH, movetime_ms: int = DEFAULT_MOVETIME_MS, threads: int = DEFAULT_THREADS, hash_mb: int = DEFAULT_HASH_MB, skill: int = DEFAULT_SKILL) -> None:
        resolved = resolve_stockfish_path(path)
        if resolved is None:
            try:
                QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
                QtWidgets.QMessageBox.warning(
                    None, "Stockfish not found",
                    "Couldn't locate the Stockfish engine.\n\n"
                    "Download from https://stockfishchess.org/download/ "
                    "and select the .exe in the next dialog."
                )
                fname, _ = QtWidgets.QFileDialog.getOpenFileName(
                    None, "Locate Stockfish executable", "",
                    "Executables (*.exe);;All files (*.*)"
                )
                if fname and os.path.isfile(fname):
                    resolved = fname
            except Exception:
                pass

        if resolved is None:
            log.failure("Stockfish not found")
            sys.exit(1)

        self.path = resolved
        log.info(f"Using Engine -> {resolved}")
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(resolved)
        except Exception as e:
            log.failure(f"Failed to launch Stockfish -> {e}")
            sys.exit(1)

        self.depth = depth
        self.movetime_ms = movetime_ms
        self._configure(threads, hash_mb, skill)

    def _configure(self, threads: int, hash_mb: int, skill: int) -> None:
        try:
            self.engine.configure({
                "Threads": threads,
                "Hash": hash_mb,
                "Skill Level": skill,
            })
        except Exception as e:
            log.failure(e)

    def set_options(self, depth: int, movetime_ms: int, threads: int, hash_mb: int, skill: int) -> None:
        self.depth = depth
        self.movetime_ms = movetime_ms
        self._configure(threads, hash_mb, skill)

    def analyse(self, board: chess.Board) -> Tuple[Optional[chess.Move], Optional[chess.engine.PovScore], List[chess.Move]]:
        try:
            limit = chess.engine.Limit(depth=self.depth,
                                       time=self.movetime_ms / 1000.0)
            info = self.engine.analyse(board, limit)
            pv = info.get("pv", [])
            move = pv[0] if pv else None
            return move, info.get("score"), pv
        except Exception as e:
            log.failure(e)
            return None, None, []

    def close(self) -> None:
        try:
            self.engine.quit()
        except Exception:
            pass
