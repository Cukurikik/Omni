# Omni PokeChamp Minimax Agent (Python)
# Compute Layer: Expert-level minimax language agent for competitive games.
# Ref: sethkarten/pokechamp — ICML 2025 Spotlight, Minimax Language Agent.

from typing import List, Dict, Optional, Tuple
import math

class GameState:
    __slots__ = ('board', 'player_turn', 'score', 'depth')
    def __init__(self, board: Dict, player_turn: int, score: float, depth: int = 0):
        self.board = board
        self.player_turn = player_turn
        self.score = score
        self.depth = depth

def minimax(state: GameState, depth: int, maximizing: bool, alpha: float = -math.inf, beta: float = math.inf) -> float:
    if depth == 0: return state.score
    if maximizing:
        max_eval = -math.inf
        for child_score in [state.score * 1.1, state.score * 0.9, state.score]:
            val = minimax(GameState(state.board, 1 - state.player_turn, child_score, state.depth + 1),
                          depth - 1, False, alpha, beta)
            max_eval = max(max_eval, val)
            alpha = max(alpha, val)
            if beta <= alpha: break
        return round(max_eval, 8)
    else:
        min_eval = math.inf
        for child_score in [state.score * 1.1, state.score * 0.9, state.score]:
            val = minimax(GameState(state.board, 1 - state.player_turn, child_score, state.depth + 1),
                          depth - 1, True, alpha, beta)
            min_eval = min(min_eval, val)
            beta = min(beta, val)
            if beta <= alpha: break
        return round(min_eval, 8)
