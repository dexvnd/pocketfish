from typing import List, Optional, Tuple
import numpy as np
import chess

from .config import EMPTY, WHITE_PIECE, BLACK_PIECE
from .vision import chess_to_grid, grid_from_board


def detect_orientation(curr_grid: np.ndarray, board: chess.Board, hint_flipped: bool) -> Tuple[bool, int, int]:
    g_unflipped = grid_from_board(board, False)
    g_flipped = grid_from_board(board, True)
    s_unflipped = int(np.sum(g_unflipped == curr_grid))
    s_flipped = int(np.sum(g_flipped == curr_grid))

    if abs(s_flipped - s_unflipped) < 4:
        chosen = hint_flipped
    else:
        chosen = s_flipped > s_unflipped

    if chosen:
        return True, s_flipped, s_unflipped
    return False, s_unflipped, s_flipped


def score_move_against_grid(move: chess.Move, prev_grid: np.ndarray, curr_grid: np.ndarray, flipped: bool, board: chess.Board) -> int:
    expected = {}
    moving_color = WHITE_PIECE if board.turn == chess.WHITE else BLACK_PIECE
    expected[chess_to_grid(move.from_square, flipped)] = EMPTY
    expected[chess_to_grid(move.to_square, flipped)] = moving_color

    if board.is_castling(move):
        if board.is_kingside_castling(move):
            rook_from = chess.H1 if board.turn == chess.WHITE else chess.H8
            rook_to = chess.F1 if board.turn == chess.WHITE else chess.F8
        else:
            rook_from = chess.A1 if board.turn == chess.WHITE else chess.A8
            rook_to = chess.D1 if board.turn == chess.WHITE else chess.D8
        expected[chess_to_grid(rook_from, flipped)] = EMPTY
        expected[chess_to_grid(rook_to, flipped)] = moving_color
    if board.is_en_passant(move):
        captured_sq = move.to_square + (-8 if board.turn == chess.WHITE else 8)
        expected[chess_to_grid(captured_sq, flipped)] = EMPTY

    score = 0
    for (r, c), want in expected.items():
        if curr_grid[r, c] == want:
            score += 2 if prev_grid[r, c] != want else 1
        else:
            score -= 2
    return score


def infer_move(prev_grid: np.ndarray, curr_grid: np.ndarray, flipped: bool, board: chess.Board) -> Optional[chess.Move]:
    if np.array_equal(prev_grid, curr_grid):
        return None
    best_move, best_score = None, -10
    for move in board.legal_moves:
        s = score_move_against_grid(move, prev_grid, curr_grid, flipped, board)
        if s > best_score:
            best_score, best_move = s, move
    return best_move if best_score >= 3 else None


def resync_board(curr_grid: np.ndarray, flipped: bool,
                 current: chess.Board) -> Optional[chess.Board]:
    cur_match = int(np.sum(grid_from_board(current, flipped) == curr_grid))

    def validate(board_after: chess.Board) -> bool:
        if not board_after.move_stack:
            return True
        last = board_after.move_stack[-1]
        piece = board_after.piece_at(last.to_square)
        if piece is None:
            return True
        expected = WHITE_PIECE if piece.color == chess.WHITE else BLACK_PIECE
        r, c = chess_to_grid(last.to_square, flipped)
        return curr_grid[r, c] == expected

    one_ply: List[Tuple[int, chess.Board]] = []
    for m in list(current.legal_moves):
        b = current.copy()
        b.push(m)
        match = int(np.sum(grid_from_board(b, flipped) == curr_grid))
        one_ply.append((match, b))

    two_ply: List[Tuple[int, chess.Board]] = []
    for _, b in one_ply:
        for m2 in list(b.legal_moves):
            b2 = b.copy()
            b2.push(m2)
            match = int(np.sum(grid_from_board(b2, flipped) == curr_grid))
            two_ply.append((match, b2))

    three_ply: List[Tuple[int, chess.Board]] = []
    if cur_match < 60:
        for _, b in sorted(two_ply, key=lambda x: -x[0])[:30]:
            for m3 in list(b.legal_moves):
                b3 = b.copy()
                b3.push(m3)
                match = int(np.sum(grid_from_board(b3, flipped) == curr_grid))
                three_ply.append((match, b3))

    one_ply_valid = [(s, b) for s, b in one_ply if validate(b)]
    two_ply_valid = [(s, b) for s, b in two_ply if validate(b)]
    three_ply_valid = [(s, b) for s, b in three_ply if validate(b)]

    best_one = max(one_ply_valid, key=lambda x: x[0]) if one_ply_valid else (-1, None)
    best_two = max(two_ply_valid, key=lambda x: x[0]) if two_ply_valid else (-1, None)
    best_three = max(three_ply_valid, key=lambda x: x[0]) if three_ply_valid else (-1, None)

    if best_one[0] >= 56 and best_one[0] > cur_match:
        return best_one[1]
    if best_two[0] >= 56 and best_two[0] > cur_match + 1:
        return best_two[1]
    if best_three[0] >= 56 and best_three[0] > cur_match + 2:
        return best_three[1]

    if best_one[0] >= 52 and best_one[0] > cur_match + 2:
        return best_one[1]

    if cur_match >= 54:
        return current
    return None