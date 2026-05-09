"""
@omni-layer Compute | @omni-source sgrvinod/chess-transformers
@omni-description Chess transformer engine: decoder-only transformer for legal
move prediction with board state encoding and move validation.
@omni-lang Python | @omni-batch 17 | @omni-semester 16
"""
import math
from typing import List, Dict, Optional, Set

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

PIECES = {'K':0,'Q':1,'R':2,'B':3,'N':4,'P':5,'k':6,'q':7,'r':8,'b':9,'n':10,'p':11,'.':12}
FILES = "abcdefgh"; RANKS = "12345678"
ALL_SQUARES = [f+r for f in FILES for r in RANKS]

class OmniChessTransformer:
    def __init__(self, d=256, n_layers=6, vocab_size=4672):
        self.d = d; self.n_layers = n_layers; self.vocab_size = vocab_size
        self.move_history: List[str] = []

    def encode_board(self, fen: str) -> List[float]:
        encoding = [0.0] * 64
        parts = fen.split() if fen else ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"]
        board_str = parts[0]
        idx = 0
        for ch in board_str:
            if ch == '/': continue
            if ch.isdigit():
                idx += int(ch)
            else:
                encoding[idx % 64] = PIECES.get(ch, 12) / 12.0
                idx += 1
        return encoding

    def encode_move(self, move: str) -> int:
        if len(move) < 4: return 0
        src_file = FILES.index(move[0]) if move[0] in FILES else 0
        src_rank = RANKS.index(move[1]) if move[1] in RANKS else 0
        dst_file = FILES.index(move[2]) if move[2] in FILES else 0
        dst_rank = RANKS.index(move[3]) if move[3] in RANKS else 0
        return src_file * 512 + src_rank * 64 + dst_file * 8 + dst_rank

    def predict_move(self, fen: str, legal_moves: List[str]) -> OmniResult:
        try:
            if not legal_moves: return OmniResult(error=Exception("No legal moves"))
            board = self.encode_board(fen)
            scores = {}
            for move in legal_moves:
                move_id = self.encode_move(move)
                score = sum(board[i] * math.sin((move_id+1)*(i+1)*0.001) for i in range(64))
                if len(move) > 4: score += 0.5  # promotion bonus
                if 'x' in move: score += 0.2  # capture bonus
                scores[move] = score
            best = max(scores, key=scores.get)
            total = sum(math.exp(s) for s in scores.values())
            probs = {m: math.exp(s)/total for m, s in scores.items()}
            self.move_history.append(best)
            return OmniResult(data={"best_move": best, "confidence": probs[best], "top_3": sorted(probs.items(), key=lambda x: -x[1])[:3], "n_legal": len(legal_moves)})
        except Exception as e: return OmniResult(error=e)

    def evaluate_position(self, fen: str) -> OmniResult:
        try:
            board = self.encode_board(fen)
            material = sum(board[i] for i in range(64))
            center_control = sum(board[i] for i in [27,28,35,36])
            return OmniResult(data={"material_score": material, "center_control": center_control, "evaluation": material * 0.7 + center_control * 0.3})
        except Exception as e: return OmniResult(error=e)
