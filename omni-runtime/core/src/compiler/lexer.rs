#[derive(Debug, Clone, PartialEq)]
pub enum Token {
    // Keywords
    Let, Mut, Const, Fn, Pub, Async, Await, If, Else, For, In, Yield,
    Immutable, Val, Mutable, Var,
    Return, Struct, Class, Extends, Implements, Abstract, Override, Extension,
    Spawn, UnsafeZone, Export, Import, From, As, View, Query, Do, MacroRules,
    While, Match, Enum, Break, Continue,
    New, Typeof, Try, Trait, Impl,
    
    // Types
    Int, Float, StringTy, Bool, Void,
    
    // Identifiers & Literals
    Ident(String),
    IntLit(i64),
    FloatLit(f64),
    StringLit(String),
    BoolLit(bool),
    // Template literal: `hello ${name}!` → segments of (is_expr, content)
    TemplateLiteral(Vec<(bool, String)>),
    
    // Symbols
    Plus, Minus, Star, Slash, Eq, EqEq, BangEq, Lt, Gt, LtEq, GtEq,
    Dot, DotStar, DotPlus, // Tensors: .* , .+
    DotDot, // .. Range
    Pipe, // |>
    Arrow, // ->
    FatArrow, // =>
    Colon, DoubleColon,
    Semicolon,
    Comma,
    At, // @ Decorator
    Bang, // ! Macro
    Question, // ? Option/Error
    And, // &&
    Or, // ||
    Percent, // %
    PlusEq, // +=
    MinusEq, // -=
    StarEq, // *=
    SlashEq, // /=
    DotDotDot, // ... spread
    
    // Brackets
    LParen, RParen,
    LBrace, RBrace,
    LBracket, RBracket,
    
    // UI JSX specifics might reuse < and >, but we define them for clarity
    // For now we map them to Lt/Gt contextually
    
    EOF,
}

pub struct Lexer<'a> {
    input: std::str::Chars<'a>,
    current_char: Option<char>,
}

impl<'a> Lexer<'a> {
    pub fn new(input: &'a str) -> Self {
        let mut chars = input.chars();
        let current_char = chars.next();
        Self {
            input: chars,
            current_char,
        }
    }

    fn advance(&mut self) {
        self.current_char = self.input.next();
    }

    fn skip_whitespace(&mut self) {
        while let Some(c) = self.current_char {
            if c.is_whitespace() {
                self.advance();
            } else {
                break;
            }
        }
    }

    pub fn next_token(&mut self) -> Token {
        self.skip_whitespace();

        if let Some(c) = self.current_char {
            match c {
                '*' => {
                    self.advance();
                    if self.current_char == Some('=') {
                        self.advance();
                        Token::StarEq
                    } else {
                        Token::Star
                    }
                },
                '/' => {
                    self.advance();
                    if self.current_char == Some('/') {
                        // Single-line comment: skip until end of line
                        while let Some(ch) = self.current_char {
                            if ch == '\n' { break; }
                            self.advance();
                        }
                        self.advance(); // skip the newline
                        return self.next_token(); // recurse for next real token
                    } else if self.current_char == Some('*') {
                        // Multi-line comment: skip until */
                        self.advance(); // skip *
                        loop {
                            match self.current_char {
                                Some('*') => {
                                    self.advance();
                                    if self.current_char == Some('/') {
                                        self.advance();
                                        break;
                                    }
                                }
                                Some(_) => self.advance(),
                                None => break,
                            }
                        }
                        return self.next_token(); // recurse
                    } else if self.current_char == Some('=') {
                        self.advance();
                        Token::SlashEq
                    } else {
                        Token::Slash
                    }
                },
                '+' => {
                    self.advance();
                    if self.current_char == Some('=') {
                        self.advance();
                        Token::PlusEq
                    } else {
                        Token::Plus
                    }
                },
                '-' => { 
                    self.advance(); 
                    if self.current_char == Some('>') {
                        self.advance();
                        Token::Arrow
                    } else if self.current_char == Some('=') {
                        self.advance();
                        Token::MinusEq
                    } else {
                        Token::Minus 
                    }
                },
                '|' => {
                    self.advance();
                    if self.current_char == Some('>') {
                        self.advance();
                        Token::Pipe
                    } else if self.current_char == Some('|') {
                        self.advance();
                        Token::Or
                    } else {
                        Token::Ident("|".to_string()) // fallback
                    }
                },
                '.' => {
                    self.advance();
                    if self.current_char == Some('*') {
                        self.advance();
                        Token::DotStar
                    } else if self.current_char == Some('+') {
                        self.advance();
                        Token::DotPlus
                    } else if self.current_char == Some('.') {
                        self.advance();
                        if self.current_char == Some('.') {
                            self.advance();
                            Token::DotDotDot
                        } else {
                            Token::DotDot
                        }
                    } else {
                        Token::Dot
                    }
                },
                '@' => { self.advance(); Token::At },
                '!' => {
                    self.advance();
                    if self.current_char == Some('=') {
                        self.advance();
                        Token::BangEq
                    } else {
                        Token::Bang
                    }
                },
                '&' => {
                    self.advance();
                    if self.current_char == Some('&') {
                        self.advance();
                        Token::And
                    } else {
                        Token::Ident("&".to_string()) // single & fallback
                    }
                },
                '%' => { self.advance(); Token::Percent },
                ':' => {
                    self.advance();
                    if self.current_char == Some(':') {
                        self.advance();
                        Token::DoubleColon
                    } else {
                        Token::Colon
                    }
                },
                '=' => {
                    self.advance();
                    if self.current_char == Some('>') {
                        self.advance();
                        Token::FatArrow
                    } else if self.current_char == Some('=') {
                        self.advance();
                        Token::EqEq
                    } else {
                        Token::Eq
                    }
                },
                ';' => { self.advance(); Token::Semicolon },
                ',' => { self.advance(); Token::Comma },
                '(' => { self.advance(); Token::LParen },
                ')' => { self.advance(); Token::RParen },
                '{' => { self.advance(); Token::LBrace },
                '}' => { self.advance(); Token::RBrace },
                '[' => { self.advance(); Token::LBracket },
                ']' => { self.advance(); Token::RBracket },
                '<' => {
                    self.advance();
                    if self.current_char == Some('=') {
                        self.advance();
                        Token::LtEq
                    } else {
                        Token::Lt
                    }
                },
                '>' => {
                    self.advance();
                    if self.current_char == Some('=') {
                        self.advance();
                        Token::GtEq
                    } else {
                        Token::Gt
                    }
                },

                '?' => { self.advance(); Token::Question },
                '"' => {
                    self.advance();
                    let mut s = String::new();
                    while let Some(ch) = self.current_char {
                        if ch == '"' { break; }
                        if ch == '\\' {
                            self.advance();
                            match self.current_char {
                                Some('n') => { s.push('\n'); self.advance(); },
                                Some('t') => { s.push('\t'); self.advance(); },
                                Some('\\') => { s.push('\\'); self.advance(); },
                                Some('"') => { s.push('"'); self.advance(); },
                                Some(c) => { s.push('\\'); s.push(c); self.advance(); },
                                None => {},
                            }
                            continue;
                        }
                        s.push(ch);
                        self.advance();
                    }
                    self.advance();
                    Token::StringLit(s)
                },
                // ── Template Literal: `hello ${name}!` ──
                '`' => {
                    self.advance();
                    let mut segments: Vec<(bool, String)> = Vec::new();
                    let mut current_str = String::new();
                    while let Some(ch) = self.current_char {
                        if ch == '`' { 
                            self.advance();
                            break; 
                        }
                        if ch == '$' {
                            self.advance();
                            if self.current_char == Some('{') {
                                // Push accumulated string part
                                if !current_str.is_empty() {
                                    segments.push((false, current_str.clone()));
                                    current_str.clear();
                                }
                                self.advance(); // skip '{'
                                // Collect expression until matching '}'
                                let mut expr_str = String::new();
                                let mut brace_depth = 1;
                                while let Some(ec) = self.current_char {
                                    if ec == '{' { brace_depth += 1; }
                                    if ec == '}' {
                                        brace_depth -= 1;
                                        if brace_depth == 0 {
                                            self.advance();
                                            break;
                                        }
                                    }
                                    expr_str.push(ec);
                                    self.advance();
                                }
                                segments.push((true, expr_str));
                            } else {
                                current_str.push('$');
                            }
                        } else if ch == '\\' {
                            self.advance();
                            match self.current_char {
                                Some('n') => { current_str.push('\n'); self.advance(); },
                                Some('t') => { current_str.push('\t'); self.advance(); },
                                Some('`') => { current_str.push('`'); self.advance(); },
                                Some('$') => { current_str.push('$'); self.advance(); },
                                Some(c) => { current_str.push('\\'); current_str.push(c); self.advance(); },
                                None => {},
                            }
                        } else {
                            current_str.push(ch);
                            self.advance();
                        }
                    }
                    if !current_str.is_empty() {
                        segments.push((false, current_str));
                    }
                    Token::TemplateLiteral(segments)
                },
                c if c.is_alphabetic() || c == '_' => {
                    let mut s = String::new();
                    while let Some(ch) = self.current_char {
                        if ch.is_alphanumeric() || ch == '_' {
                            s.push(ch);
                            self.advance();
                        } else {
                            break;
                        }
                    }
                    match s.as_str() {
                        "let" => Token::Let,
                        "mut" => Token::Mut,
                        "const" => Token::Const,
                        "immutable" => Token::Immutable,
                        "val" => Token::Val,
                        "mutable" => Token::Mutable,
                        "var" => Token::Var,
                        "fn" => Token::Fn,
                        "pub" => Token::Pub,
                        "async" => Token::Async,
                        "await" => Token::Await,
                        "if" => Token::If,
                        "else" => Token::Else,
                        "for" => Token::For,
                        "in" => Token::In,
                        "yield" => Token::Yield,
                        "return" => Token::Return,
                        "struct" => Token::Struct,
                        "class" => Token::Class,
                        "extends" => Token::Extends,
                        "implements" => Token::Implements,
                        "abstract" => Token::Abstract,
                        "override" => Token::Override,
                        "extension" => Token::Extension,
                        "spawn" => Token::Spawn,
                        "unsafe_zone" => Token::UnsafeZone,
                        "export" => Token::Export,
                        "import" => Token::Import,
                        "from" => Token::From,
                        "as" => Token::As,
                        "view" => Token::View,
                        "query" => Token::Query,
                        "do" => Token::Do,
                        "macro_rules" => Token::MacroRules,
                        "while" => Token::While,
                        "match" => Token::Match,
                        "enum" => Token::Enum,
                        "break" => Token::Break,
                        "continue" => Token::Continue,
                        "new" => Token::New,
                        "typeof" => Token::Typeof,
                        "try" => Token::Try,
                        "trait" => Token::Trait,
                        "impl" => Token::Impl,
                        "Int" => Token::Int,
                        "Float" => Token::Float,
                        "String" => Token::StringTy,
                        "Bool" => Token::Bool,
                        "Void" => Token::Void,
                        "true" => Token::BoolLit(true),
                        "false" => Token::BoolLit(false),
                        _ => Token::Ident(s),
                    }
                },
                c if c.is_numeric() => {
                    let mut s = String::new();
                    let mut is_float = false;
                    while let Some(ch) = self.current_char {
                        if ch.is_numeric() || ch == '_' {
                            if ch != '_' { s.push(ch); }
                            self.advance();
                        } else if ch == '.' && !is_float {
                            // Peek ahead: if next char is also '.', this is a range (0..5), not a float
                            let mut peek_iter = self.input.clone();
                            let next_after_dot = peek_iter.next();
                            if next_after_dot == Some('.') {
                                break; // Don't consume the dot — it's a range operator
                            }
                            s.push(ch);
                            is_float = true;
                            self.advance();
                        } else {
                            break;
                        }
                    }
                    if is_float {
                        Token::FloatLit(s.parse().unwrap_or(0.0))
                    } else {
                        Token::IntLit(s.parse().unwrap_or(0))
                    }
                },
                _ => {
                    self.advance();
                    // Skip unknown chars, don't kill the stream
                    return self.next_token();
                }
            }
        } else {
            Token::EOF
        }
    }
}
