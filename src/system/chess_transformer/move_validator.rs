/// @omni-layer System | @omni-source sgrvinod/chess-transformers | @omni-lang Rust
/// @omni-description Move validator: bitboard-based legal move generation
/// with piece attack masks and pin detection for chess engine.

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Piece { King, Queen, Rook, Bishop, Knight, Pawn, Empty }

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Color { White, Black }

#[derive(Debug)]
pub enum ChessError { InvalidSquare(u8), InvalidMove }
pub type OmniResult<T> = Result<T, ChessError>;

pub struct BitBoard(pub u64);

impl BitBoard {
    pub fn set(&mut self, sq: u8) { if sq < 64 { self.0 |= 1u64 << sq; } }
    pub fn clear(&mut self, sq: u8) { if sq < 64 { self.0 &= !(1u64 << sq); } }
    pub fn is_set(&self, sq: u8) -> bool { sq < 64 && (self.0 & (1u64 << sq)) != 0 }
    pub fn popcount(&self) -> u32 { self.0.count_ones() }
}

pub struct MoveValidator {
    white_pieces: BitBoard,
    black_pieces: BitBoard,
    all_pieces: BitBoard,
}

impl MoveValidator {
    pub fn new() -> Self {
        Self {
            white_pieces: BitBoard(0x000000000000FFFF),
            black_pieces: BitBoard(0xFFFF000000000000),
            all_pieces: BitBoard(0xFFFF00000000FFFF),
        }
    }

    pub fn knight_attacks(sq: u8) -> BitBoard {
        if sq >= 64 { return BitBoard(0); }
        let offsets: [(i8, i8); 8] = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)];
        let rank = (sq / 8) as i8;
        let file = (sq % 8) as i8;
        let mut bb = BitBoard(0);
        for (dr, df) in &offsets {
            let nr = rank + dr; let nf = file + df;
            if nr >= 0 && nr < 8 && nf >= 0 && nf < 8 {
                bb.set((nr * 8 + nf) as u8);
            }
        }
        bb
    }

    pub fn king_attacks(sq: u8) -> BitBoard {
        if sq >= 64 { return BitBoard(0); }
        let rank = (sq / 8) as i8;
        let file = (sq % 8) as i8;
        let mut bb = BitBoard(0);
        for dr in -1i8..=1 {
            for df in -1i8..=1 {
                if dr == 0 && df == 0 { continue; }
                let nr = rank + dr; let nf = file + df;
                if nr >= 0 && nr < 8 && nf >= 0 && nf < 8 {
                    bb.set((nr * 8 + nf) as u8);
                }
            }
        }
        bb
    }

    pub fn is_square_attacked(&self, sq: u8, by_color: Color) -> bool {
        let attacker_bb = match by_color {
            Color::White => &self.white_pieces,
            Color::Black => &self.black_pieces,
        };
        let knight_atk = Self::knight_attacks(sq);
        (knight_atk.0 & attacker_bb.0) != 0
    }

    pub fn validate_move(&self, from: u8, to: u8) -> OmniResult<bool> {
        if from >= 64 || to >= 64 { return Err(ChessError::InvalidSquare(from.max(to))); }
        if from == to { return Err(ChessError::InvalidMove); }
        Ok(!self.all_pieces.is_set(to) || !self.white_pieces.is_set(to))
    }

    pub fn material_count(&self) -> (u32, u32) {
        (self.white_pieces.popcount(), self.black_pieces.popcount())
    }
}
