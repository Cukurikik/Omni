// Lexer untuk tokenizer string ke struktur data (OMNI-PRIME)
#[derive(Debug, PartialEq, Clone)]
pub enum Token {
    // Keywords
    Fn, Let, Struct, Import, Await, Spawn, If, Return, True, False,
    
    // Identifiers and Literals
    Ident(String),
    Int(i64),
    Str(String),
    
    // Operators
    Assign,          // =
    Arrow,           // ->
    NullCoalesce,    // ??
    OptChain,        // ?.
    Question,        // ?
    EqEq,            // ==
    
    // Punctuation
    Colon,           // :
    LBrace,          // {
    RBrace,          // }
    LParen,          // (
    RParen,          // )
    LBracket,        // [
    RBracket,        // ]
    Dot,             // .
    Comma,           // ,
    
    EOF,
}

pub struct Lexer<'a> {
    content: &'a str,
    pos: usize,
}

impl<'a> Lexer<'a> {
    pub fn new(content: &'a str) -> Self {
        Self { content, pos: 0 }
    }
    
    pub fn tokenize(&mut self) -> Vec<Token> {
        let mut tokens = Vec::new();
        let bytes = self.content.as_bytes();
        
        while self.pos < bytes.len() {
            let b = bytes[self.pos];
            if b.is_ascii_whitespace() {
                 self.pos += 1;
                 continue;
            }
            
            // Komentar
            if b == b'/' && self.pos + 1 < bytes.len() && bytes[self.pos+1] == b'/' {
                 while self.pos < bytes.len() && bytes[self.pos] != b'\n' {
                     self.pos += 1;
                 }
                 continue;
            }
            
            // Mengendus Sintaks Mematikan: Null Safety, Spawn Coalescing
            if b == b'?' && self.pos + 1 < bytes.len() {
                if bytes[self.pos+1] == b'?' {
                     tokens.push(Token::NullCoalesce);
                     self.pos += 2;
                     continue;
                } else if bytes[self.pos+1] == b'.' {
                     tokens.push(Token::OptChain);
                     self.pos += 2;
                     continue;
                }
            }
            
            if b == b'-' && self.pos + 1 < bytes.len() && bytes[self.pos+1] == b'>' {
                 tokens.push(Token::Arrow);
                 self.pos += 2;
                 continue;
            }
            
            // Scan structural punctuation
            match b {
                b'{' => { tokens.push(Token::LBrace); self.pos += 1; continue; }
                b'}' => { tokens.push(Token::RBrace); self.pos += 1; continue; }
                b'[' => { tokens.push(Token::LBracket); self.pos += 1; continue; }
                b']' => { tokens.push(Token::RBracket); self.pos += 1; continue; }
                b'(' => { tokens.push(Token::LParen); self.pos += 1; continue; }
                b')' => { tokens.push(Token::RParen); self.pos += 1; continue; }
                b':' => { tokens.push(Token::Colon); self.pos += 1; continue; }
                b'=' => { 
                     if self.pos+1 < bytes.len() && bytes[self.pos+1] == b'=' {
                         tokens.push(Token::EqEq); self.pos+=2; continue;
                     }
                     tokens.push(Token::Assign); self.pos += 1; continue; 
                }
                b'.' => { tokens.push(Token::Dot); self.pos += 1; continue; }
                b',' => { tokens.push(Token::Comma); self.pos += 1; continue; }
                b'?' => { tokens.push(Token::Question); self.pos += 1; continue; }
                _ => {}
            }
            
            // Melangkah maju dengan brutal untuk iterasi OMNI token builder
            self.pos += 1;
        }
        tokens.push(Token::EOF);
        tokens
    }
}
