import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(PACKAGE_DIR, "assets", "logo.png")

STOCKFISH_PATH = os.path.join(PACKAGE_DIR, "assets", "stockfish.exe")

DEFAULT_DEPTH = 14
DEFAULT_SKILL = 10
DEFAULT_THREADS = 2
DEFAULT_HASH_MB = 128
DEFAULT_MOVETIME_MS = 300

CAPTURE_INTERVAL = 0.12

LIGHT_SQUARE_BGR = (181, 217, 238)
DARK_SQUARE_BGR = (88, 150, 118)
COLOR_TOLERANCE = 35
MIN_BOARD_SIZE = 250

EMPTY = 0
WHITE_PIECE = 1
BLACK_PIECE = 2
