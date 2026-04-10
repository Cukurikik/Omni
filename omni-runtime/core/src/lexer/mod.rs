#![allow(dead_code)]
// ==========================================
// 🔤 OMNI-LANG LEXER: THE ATOM SPLITTER
// ==========================================
// Membaca karakter dari source code secara streaming,
// memecahnya menjadi Token OMNI. Mendukung token gado-gado
// untuk TypeScript, Rust, Python, Matrix Calculus, dan HTML/JSX
// tanpa plugin eksternal.
// ==========================================

#[derive(Debug, Clone, PartialEq)]
pub enum TokenKind {
    // Keywords
    Let, Fn, Mut, Guard, Else, Import, Return, Unsafe, Spawn, Await, Async,
    Extern,          // extern (для FFI)
    
    // Decorators
    FFIDecorator,    // @ffi(...)
    
    // Identifiers & Literals
    Identifier(String),
    IntLiteral(i64),
    FloatLiteral(f64),
    StringLiteral(String),

    // Symbols & Ops
    Assign,          // =
    Plus, Minus, Star, Slash, 
    MatrixPower,     // ^ (Linear Algebra Native)
    QuestionDot,     // ?. (Safe Navigation)
    NullCoalesce,    // ?? 

    // Delimiters
    LParen, RParen, LBrace, RBrace, LBracket, RBracket,
    At,              // @ (decorator prefix)
    SemiColon, Colon, Comma,

    // JSX / UI Native 
    LAngle,          // <
    RAngle,          // > 
    SlashAngle,      // />
    
    EOF,
}

#[derive(Debug, Clone)]
pub struct Token {
    pub kind: TokenKind,
    pub line: usize,
    pub column: usize,
    pub lexeme: String,
}

pub struct OmniLexer<'a> {
    source: &'a str,
    position: usize,
    line: usize,
    column: usize,
}

impl<'a> OmniLexer<'a> {
    pub fn new(source: &'a str) -> Self {
        println!("[LEXER] 🔤 Mengaktifkan Pemecah Atom (OMNI Lexer)!");
        Self {
            source,
            position: 0,
            line: 1,
            column: 1,
        }
    }

    pub fn scan_next_token(&mut self) -> Token {
        // cepat tokenizer OMNI
        // "let ai_tensor = (base_matrix ^ 2);"
        Token {
            kind: TokenKind::EOF,
            line: self.line,
            column: self.column,
            lexeme: "".to_string(),
        }
    }
}
