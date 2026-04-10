use super::ast::*;
use super::lexer::*;

pub struct Parser<'a> {
    lexer: Lexer<'a>,
    current_token: Token,
}

impl<'a> Parser<'a> {
    pub fn new(mut lexer: Lexer<'a>) -> Self {
        let current_token = lexer.next_token();
        Self { lexer, current_token }
    }

    fn advance(&mut self) {
        self.current_token = self.lexer.next_token();
    }

    fn eat(&mut self, token_type: Token) -> bool {
        if std::mem::discriminant(&self.current_token) == std::mem::discriminant(&token_type) {
            self.advance();
            true
        } else {
            false
        }
    }

    /// Mengkonsumsi token dan mengembalikan nilai String dari identifier
    fn eat_ident(&mut self) -> Option<String> {
        if let Token::Ident(s) = self.current_token.clone() {
            self.advance();
            Some(s)
        } else {
            None
        }
    }

    pub fn parse_program(&mut self) -> OmniProgram {
        let mut statements = Vec::new();
        while self.current_token != Token::EOF {
            if let Some(stmt) = self.parse_statement() {
                statements.push(stmt);
            } else {
                self.advance();
            }
        }
        OmniProgram { statements }
    }

    // ═══════════════════════════════════════════
    // STATEMENT PARSING — Seluruh 15 Paradigma
    // ═══════════════════════════════════════════

    fn parse_statement(&mut self) -> Option<Stmt> {
        // OMNI Blueprint: Skip decorators (e.g. @compute::julia_simd)
        while self.current_token == Token::At {
            self.advance();
            // Eat namespace parts if it has ::
            while let Token::Ident(_) = self.current_token {
                self.advance();
                if self.current_token == Token::DoubleColon {
                    self.advance();
                } else {
                    break;
                }
            }
        }

        match &self.current_token {
            Token::Let | Token::Mut | Token::Immutable | Token::Mutable | Token::Val | Token::Var => self.parse_let_decl(),
            Token::Const               => self.parse_const_decl(),
            Token::Fn | Token::Pub | Token::Async => self.parse_function_def(),
            Token::Struct              => self.parse_struct_def(),
            Token::Export              => self.parse_export_or_view(),
            Token::View                => self.parse_view_def(),
            Token::Spawn               => self.parse_spawn(),
            Token::Class               => self.parse_class_def(),
            Token::Extension           => self.parse_extension_def(),
            Token::Return              => self.parse_return(),
            Token::Yield               => self.parse_yield(),
            Token::If                  => self.parse_if(),
            Token::For                 => self.parse_for_in(),
            Token::Import              => self.parse_import(),
            Token::Trait               => self.parse_trait_def(),
            Token::Impl                => self.parse_impl_def(),
            // Phase 2
            Token::While               => self.parse_while(),
            Token::Enum                => self.parse_enum_def(),
            Token::UnsafeZone          => self.parse_unsafe_zone(),
            Token::Break               => { self.advance(); self.eat(Token::Semicolon); Some(Stmt::Break) },
            Token::Continue            => { self.advance(); self.eat(Token::Semicolon); Some(Stmt::Continue) },
            _ => {
                // Check for polyglot block: use::lang { ... }
                if let Token::Ident(name) = &self.current_token {
                    if name == "use" {
                        // Lookahead manually or just match
                        self.advance(); // eat 'use'
                        if self.eat(Token::DoubleColon) {
                            if let Token::Ident(lang) = self.current_token.clone() {
                                self.advance(); // eat lang
                                let body = self.parse_block();
                                return Some(Stmt::PolyglotBlock { lang, body });
                            } else {
                                eprintln!("Expected language identifier after 'use::', found {:?}", self.current_token);
                            }
                        }
                        // If it wasn't double colon, it was just the identifier "use". 
                        // Our parser doesn't perfectly backtrack, but we don't have variables named 'use' ideally.
                        // Actually, to be safe we'll just fail parsing if it's not DoubleColon.
                    }
                }

                // Check for array destructuring: let [a, b] = expr; (when 'let' wasn't matched because next is '[')
                let expr = self.parse_expression();
                // Check for compound assignment: expr += value;
                match &self.current_token {
                    Token::PlusEq | Token::MinusEq | Token::StarEq | Token::SlashEq => {
                        let op = match &self.current_token {
                            Token::PlusEq => "+=".to_string(),
                            Token::MinusEq => "-=".to_string(),
                            Token::StarEq => "*=".to_string(),
                            Token::SlashEq => "/=".to_string(),
                            _ => unreachable!(),
                        };
                        if let Expr::Identifier(name) = expr {
                            self.advance(); // eat compound op
                            let value = self.parse_expression();
                            self.eat(Token::Semicolon);
                            return Some(Stmt::CompoundAssign { target: name, op, value });
                        }
                    }
                    // Normal assignment: expr = value;
                    Token::Eq => {
                        if let Expr::Identifier(name) = expr {
                            self.advance(); // eat =
                            let value = self.parse_expression();
                            self.eat(Token::Semicolon);
                            return Some(Stmt::Assign { target: name, value });
                        }
                    }
                    _ => {}
                }
                self.eat(Token::Semicolon);
                Some(Stmt::ExprStmt(expr))
            }
        }
    }

    // ── immutable val / mutable var / let / mut ──
    fn parse_let_decl(&mut self) -> Option<Stmt> {
        let mut is_mut = false;
        
        // OMNI Blueprint Characteristic Syntax
        if self.eat(Token::Immutable) {
            self.eat(Token::Val);
            is_mut = false;
        } else if self.eat(Token::Mutable) {
            self.eat(Token::Var);
            is_mut = true;
        } else if self.current_token == Token::Let {
            self.advance(); // eat 'let'
            // Check for 'mut' after 'let'
            if self.eat(Token::Mut) {
                is_mut = true;
            }
        } else if self.eat(Token::Mut) || self.eat(Token::Var) {
            is_mut = true;
        } else {
            let _ = self.eat(Token::Val);
        }

        // Check for array destructuring: let [a, b] = expr;
        if self.current_token == Token::LBracket {
            self.advance(); // eat '['
            let mut names = Vec::new();
            while self.current_token != Token::RBracket && self.current_token != Token::EOF {
                if let Token::Ident(name) = &self.current_token {
                    names.push(name.clone());
                    self.advance();
                } else {
                    break;
                }
                if self.current_token == Token::Comma {
                    self.advance();
                }
            }
            self.eat(Token::RBracket);
            if self.eat(Token::Eq) {
                let expr = self.parse_expression();
                self.eat(Token::Semicolon);
                return Some(Stmt::ArrayDestructure { names, expr });
            }
        }

        if let Some(id) = self.eat_ident() {
            let mut ty = None;
            if self.eat(Token::Colon) {
                ty = Some(self.parse_type());
            }
            if self.eat(Token::Eq) {
                let expr = self.parse_expression();
                self.eat(Token::Semicolon);
                return Some(Stmt::LetDecl { is_mut, id, ty, expr });
            }
        }
        None
    }

    // ── const ──
    fn parse_const_decl(&mut self) -> Option<Stmt> {
        self.eat(Token::Const);
        if let Some(id) = self.eat_ident() {
            let mut ty = Type::Void;
            if self.eat(Token::Colon) {
                ty = self.parse_type();
            }
            if self.eat(Token::Eq) {
                let expr = self.parse_expression();
                self.eat(Token::Semicolon);
                return Some(Stmt::ConstDecl { id, ty, expr });
            }
        }
        None
    }

    // ── fn / pub fn / async fn / pub async fn ──
    fn parse_function_def(&mut self) -> Option<Stmt> {
        let is_pub = self.eat(Token::Pub);
        let is_async = self.eat(Token::Async);
        self.eat(Token::Fn);

        if let Some(name) = self.eat_ident() {
            self.eat(Token::LParen);
            let params = self.parse_param_list();
            self.eat(Token::RParen);

            let mut return_ty = Type::Void;
            if self.eat(Token::Arrow) {
                return_ty = self.parse_type();
            }

            let body = if self.current_token == Token::Semicolon {
                self.advance(); // eat ';'
                Vec::new() // empty body for interface/trait declarations
            } else {
                self.parse_block()
            };
            
            return Some(Stmt::FunctionDef { is_pub, is_async, name, params, return_ty, body });
        }
        None
    }

    // ── struct ──
    fn parse_struct_def(&mut self) -> Option<Stmt> {
        self.eat(Token::Struct);
        // Baca decorator (jika ada @schema di depannya, sudah di-skip oleh parse_statement)
        if let Some(name) = self.eat_ident() {
            self.eat(Token::LBrace);
            let mut fields = Vec::new();
            while self.current_token != Token::RBrace && self.current_token != Token::EOF {
                // Baca decorator per-field
                let mut field_decorators = Vec::new();
                while self.current_token == Token::At {
                    self.advance();
                    if let Some(dec_name) = self.eat_ident() {
                        field_decorators.push(dec_name);
                    }
                }
                if let Some(f_name) = self.eat_ident() {
                    self.eat(Token::Colon);
                    let ty = self.parse_type();
                    fields.push((f_name, ty, field_decorators));
                    self.eat(Token::Comma);
                } else { break; }
            }
            self.eat(Token::RBrace);
            return Some(Stmt::StructDef { is_pub: true, name, decorators: vec![], fields });
        }
        None
    }

    // ── export fn/struct/enum/view/type/const/{ symbols } ──
    fn parse_export_or_view(&mut self) -> Option<Stmt> {
        self.eat(Token::Export);
        
        // export view Name(params) { ... }
        if self.current_token == Token::View {
            self.advance();
            if let Some(name) = self.eat_ident() {
                self.eat(Token::LParen);
                let params = self.parse_param_list();
                self.eat(Token::RParen);
                let body = self.parse_block();
                return Some(Stmt::ViewDef { is_export: true, name, params, body });
            }
            return None;
        }
        
        // export fn name(...) -> Type { ... }
        // export async fn name(...) -> Type { ... }
        if self.current_token == Token::Fn || self.current_token == Token::Async {
            let is_async = self.eat(Token::Async);
            self.eat(Token::Fn);
            if let Some(name) = self.eat_ident() {
                self.eat(Token::LParen);
                let params = self.parse_param_list();
                self.eat(Token::RParen);
                let mut return_ty = Type::Void;
                if self.eat(Token::Arrow) {
                    return_ty = self.parse_type();
                }
                let body = if self.current_token == Token::Semicolon {
                    self.advance();
                    Vec::new()
                } else {
                    self.parse_block()
                };
                return Some(Stmt::FunctionDef { is_pub: true, is_async, name, params, return_ty, body });
            }
            return None;
        }
        
        // export pub fn ... (treat pub as redundant with export)
        if self.current_token == Token::Pub {
            self.advance(); // eat 'pub'
            // Delegate back — now current_token is fn/struct/etc
            if self.current_token == Token::Fn || self.current_token == Token::Async {
                let is_async = self.eat(Token::Async);
                self.eat(Token::Fn);
                if let Some(name) = self.eat_ident() {
                    self.eat(Token::LParen);
                    let params = self.parse_param_list();
                    self.eat(Token::RParen);
                    let mut return_ty = Type::Void;
                    if self.eat(Token::Arrow) {
                        return_ty = self.parse_type();
                    }
                    let body = if self.current_token == Token::Semicolon {
                        self.advance();
                        Vec::new()
                    } else {
                        self.parse_block()
                    };
                    return Some(Stmt::FunctionDef { is_pub: true, is_async, name, params, return_ty, body });
                }
            }
            return None;
        }
        
        // export struct Name { field: Type, ... }
        if self.current_token == Token::Struct {
            self.eat(Token::Struct);
            if let Some(name) = self.eat_ident() {
                self.eat(Token::LBrace);
                let mut fields = Vec::new();
                while self.current_token != Token::RBrace && self.current_token != Token::EOF {
                    // Skip decorators
                    let mut field_decorators = Vec::new();
                    while self.current_token == Token::At {
                        self.advance();
                        if let Some(dec_name) = self.eat_ident() {
                            field_decorators.push(dec_name);
                        }
                    }
                    // Check if this is a method (fn) inside the struct
                    if self.current_token == Token::Fn || self.current_token == Token::Pub {
                        // Method inside struct — skip it for now (struct with methods)
                        if let Some(_method) = self.parse_function_def() {
                            // Methods inside structs are stored differently in a full implementation
                            // For now, just advance past them
                        }
                        continue;
                    }
                    if let Some(f_name) = self.eat_ident() {
                        self.eat(Token::Colon);
                        let ty = self.parse_type();
                        fields.push((f_name, ty, field_decorators));
                        // Eat comma or semicolon separator
                        if !self.eat(Token::Comma) {
                            self.eat(Token::Semicolon);
                        }
                    } else { break; }
                }
                self.eat(Token::RBrace);
                return Some(Stmt::StructDef { is_pub: true, name, decorators: vec![], fields });
            }
            return None;
        }

        // export enum Name { Variant1, Variant2 }
        if self.current_token == Token::Enum {
            self.eat(Token::Enum);
            if let Some(name) = self.eat_ident() {
                self.eat(Token::LBrace);
                let mut variants = Vec::new();
                while self.current_token != Token::RBrace && self.current_token != Token::EOF {
                    if let Some(variant) = self.eat_ident() {
                        variants.push(variant);
                        // Handle enum variants with values: Variant = value
                        if self.eat(Token::Eq) {
                            let _val = self.parse_expression();
                        }
                        if !self.eat(Token::Comma) { break; }
                    } else { break; }
                }
                self.eat(Token::RBrace);
                return Some(Stmt::EnumDef { name, variants });
            }
            return None;
        }

        // export type Alias = Type
        if let Token::Ident(s) = &self.current_token {
            if s == "type" {
                self.advance(); // eat 'type'
                if let Some(name) = self.eat_ident() {
                    self.eat(Token::Eq);
                    let _ty = self.parse_type();
                    self.eat(Token::Semicolon);
                    // Store as a type alias — for now emit as an empty struct placeholder
                    return Some(Stmt::StructDef { is_pub: true, name, decorators: vec!["type_alias".to_string()], fields: vec![] });
                }
            }
        }
        
        // export const Name = expr
        if self.current_token == Token::Const {
            return self.parse_const_decl();
        }

        // export { A, B, C }
        if self.eat(Token::LBrace) {
            let mut symbols = Vec::new();
            while self.current_token != Token::RBrace && self.current_token != Token::EOF {
                if let Some(id) = self.eat_ident() {
                    symbols.push(id);
                    if !self.eat(Token::Comma) { break; }
                } else { break; }
            }
            self.eat(Token::RBrace);
            self.eat(Token::Semicolon);
            return Some(Stmt::Export { symbols });
        }
        
        None
    }

    // ── view ──
    fn parse_view_def(&mut self) -> Option<Stmt> {
        let is_export = false;
        self.eat(Token::View);
        if let Some(name) = self.eat_ident() {
            self.eat(Token::LParen);
            let params = self.parse_param_list();
            self.eat(Token::RParen);
            let body = self.parse_block();
            return Some(Stmt::ViewDef { is_export, name, params, body });
        }
        None
    }

    // ── spawn ──
    fn parse_spawn(&mut self) -> Option<Stmt> {
        self.eat(Token::Spawn);
        let expr = self.parse_expression();
        self.eat(Token::Semicolon);
        Some(Stmt::Spawn(expr))
    }

    // ── class (with extends, implements, methods) ──
    fn parse_class_def(&mut self) -> Option<Stmt> {
        self.eat(Token::Class);
        if let Some(name) = self.eat_ident() {
            // Generics: class Foo<T> (opsional)
            let mut generics = Vec::new();
            if self.eat(Token::Lt) {
                while self.current_token != Token::Gt && self.current_token != Token::EOF {
                    if let Some(g) = self.eat_ident() {
                        generics.push(g);
                        self.eat(Token::Comma);
                    } else { break; }
                }
                self.eat(Token::Gt);
            }

            // extends
            let extends = if self.eat(Token::Extends) {
                self.eat_ident()
            } else { None };

            // implements
            let mut implements = Vec::new();
            if self.eat(Token::Implements) {
                loop {
                    if let Some(iface) = self.eat_ident() {
                        implements.push(iface);
                        if !self.eat(Token::Comma) { break; }
                    } else { break; }
                }
            }

            // Body: parse methods inside
            self.eat(Token::LBrace);
            let mut methods = Vec::new();
            while self.current_token != Token::RBrace && self.current_token != Token::EOF {
                if let Some(m) = self.parse_statement() {
                    methods.push(m);
                } else {
                    self.advance();
                }
            }
            self.eat(Token::RBrace);

            return Some(Stmt::ClassDef { name, generics, extends, implements, methods });
        }
        None
    }

    // ── extension (Swift Protocol Extensions) ──
    fn parse_extension_def(&mut self) -> Option<Stmt> {
        self.eat(Token::Extension);
        if let Some(target_ty) = self.eat_ident() {
            self.eat(Token::LBrace);
            let mut methods = Vec::new();
            while self.current_token != Token::RBrace && self.current_token != Token::EOF {
                if let Some(m) = self.parse_statement() {
                    methods.push(m);
                } else {
                    self.advance();
                }
            }
            self.eat(Token::RBrace);
            return Some(Stmt::ExtensionDef { target_ty, methods });
        }
        None
    }

    // ── return ──
    fn parse_return(&mut self) -> Option<Stmt> {
        self.eat(Token::Return);
        let expr = self.parse_expression();
        self.eat(Token::Semicolon);
        Some(Stmt::Return(expr))
    }

    // ── yield ──
    fn parse_yield(&mut self) -> Option<Stmt> {
        self.eat(Token::Yield);
        let expr = self.parse_expression();
        self.eat(Token::Semicolon);
        Some(Stmt::Yield(expr))
    }

    // ── if / else ──
    fn parse_if(&mut self) -> Option<Stmt> {
        self.eat(Token::If);
        let condition = self.parse_expression();
        let then_branch = self.parse_block();
        let else_branch = if self.eat(Token::Else) {
            Some(self.parse_block())
        } else {
            None
        };
        Some(Stmt::If { condition, then_branch, else_branch })
    }

    // ── for x in iterable { ... } ──
    fn parse_for_in(&mut self) -> Option<Stmt> {
        self.eat(Token::For);
        if let Some(iterator) = self.eat_ident() {
            self.eat(Token::In);
            let iterable = self.parse_expression();
            let body = self.parse_block();
            return Some(Stmt::ForIn { iterator, iterable, body });
        }
        None
    }

    // ── import { A as B, C } from "path" / import "path" ──
    fn parse_import(&mut self) -> Option<Stmt> {
        self.eat(Token::Import);
        
        let mut symbols = Vec::new();
        let mut path = String::new();

        if self.eat(Token::LBrace) {
            // import { A, B as C } from "path"
            while self.current_token != Token::RBrace && self.current_token != Token::EOF {
                if let Some(id) = self.eat_ident() {
                    let mut alias = None;
                    if self.eat(Token::As) {
                        if let Some(a) = self.eat_ident() {
                            alias = Some(a);
                        }
                    }
                    symbols.push((id, alias));
                    if !self.eat(Token::Comma) { break; }
                } else { break; }
            }
            self.eat(Token::RBrace);
            self.eat(Token::From);
            if let Token::StringLit(p) = self.current_token.clone() {
                path = p;
                self.advance();
            }
        } else {
            // import "path"
            if let Token::StringLit(p) = self.current_token.clone() {
                path = p;
                self.advance();
            }
        }

        self.eat(Token::Semicolon);
        Some(Stmt::Import { path, symbols })
    }

    // ── while condition { ... } ──
    fn parse_while(&mut self) -> Option<Stmt> {
        self.eat(Token::While);
        let condition = self.parse_expression();
        let body = self.parse_block();
        Some(Stmt::While { condition, body })
    }

    // ── enum Name { Variant1, Variant2 } ──
    fn parse_enum_def(&mut self) -> Option<Stmt> {
        self.eat(Token::Enum);
        if let Some(name) = self.eat_ident() {
            self.eat(Token::LBrace);
            let mut variants = Vec::new();
            while self.current_token != Token::RBrace && self.current_token != Token::EOF {
                if let Some(variant) = self.eat_ident() {
                    variants.push(variant);
                    if !self.eat(Token::Comma) { break; }
                } else { break; }
            }
            self.eat(Token::RBrace);
            return Some(Stmt::EnumDef { name, variants });
        }
        None
    }

    // ── unsafe_zone "name" { ... } ──
    fn parse_unsafe_zone(&mut self) -> Option<Stmt> {
        self.eat(Token::UnsafeZone);
        let mut zone_name = "default".to_string();
        if let Token::StringLit(s) = self.current_token.clone() {
            zone_name = s;
            self.advance();
        }
        let body = self.parse_block();
        Some(Stmt::UnsafeZone { name: zone_name, body })
    }

    // ── trait Name { fn method(); } ──
    fn parse_trait_def(&mut self) -> Option<Stmt> {
        self.eat(Token::Trait);
        if let Some(name) = self.eat_ident() {
            self.eat(Token::LBrace);
            let mut methods = Vec::new();
            while self.current_token != Token::RBrace && self.current_token != Token::EOF {
                if let Some(method) = self.parse_function_def() {
                    methods.push(method);
                } else {
                    self.advance();
                }
            }
            self.eat(Token::RBrace);
            return Some(Stmt::TraitDef { name, methods });
        }
        None
    }

    // ── impl Trait for Struct { fn method() {} } ──
    fn parse_impl_def(&mut self) -> Option<Stmt> {
        self.eat(Token::Impl);
        if let Some(target_or_trait) = self.eat_ident() {
            let mut trait_name = None;
            let mut target = target_or_trait.clone();

            if self.current_token == Token::For {
                self.advance(); // eat 'for'
                if let Some(real_target) = self.eat_ident() {
                    trait_name = Some(target_or_trait);
                    target = real_target;
                }
            }

            self.eat(Token::LBrace);
            let mut methods = Vec::new();
            while self.current_token != Token::RBrace && self.current_token != Token::EOF {
                if let Some(method) = self.parse_function_def() {
                    methods.push(method);
                } else {
                    self.advance();
                }
            }
            self.eat(Token::RBrace);
            return Some(Stmt::ImplDef { target, trait_name, methods });
        }
        None
    }

    // ═══════════════════════════════════════════
    // HELPER: Parameter List & Block Body
    // ═══════════════════════════════════════════

    fn parse_param_list(&mut self) -> Vec<(String, Type)> {
        let mut params = Vec::new();
        while self.current_token != Token::RParen && self.current_token != Token::EOF {
            if let Some(p_name) = self.eat_ident() {
                let ty = if self.eat(Token::Colon) {
                    self.parse_type()
                } else {
                    Type::Dynamic // Untyped parameter — infer as dynamic
                };
                params.push((p_name, ty));
                if !self.eat(Token::Comma) { break; }
            } else { break; }
        }
        params
    }

    fn parse_block(&mut self) -> Vec<Stmt> {
        self.eat(Token::LBrace);
        let mut stmts = Vec::new();
        while self.current_token != Token::RBrace && self.current_token != Token::EOF {
            if let Some(s) = self.parse_statement() {
                stmts.push(s);
            } else {
                self.advance();
            }
        }
        self.eat(Token::RBrace);
        stmts
    }

    // ═══════════════════════════════════════════
    // TYPE PARSING
    // ═══════════════════════════════════════════

    fn parse_type(&mut self) -> Type {
        match &self.current_token {
            Token::Int     => { self.advance(); Type::Int },
            Token::Float   => { self.advance(); Type::Float },
            Token::StringTy => { self.advance(); Type::String },
            Token::Bool    => { self.advance(); Type::Bool },
            Token::Ident(s) => { 
                let t = Type::Struct(s.clone()); 
                self.advance();
                t
            },
            _ => { self.advance(); Type::Void }
        }
    }

    // ═══════════════════════════════════════════
    // EXPRESSION PARSING — Recursive Descent Full
    // ═══════════════════════════════════════════

    fn parse_expression(&mut self) -> Expr {
        let mut left = self.parse_primary();

        // Loop: handle chained calls, method calls, pipe, and binary ops
        loop {
            match &self.current_token {
                // Function call: expr(args...)
                Token::LParen => {
                    self.advance();
                    let mut args = Vec::new();
                    while self.current_token != Token::RParen && self.current_token != Token::EOF {
                        args.push(self.parse_expression());
                        if !self.eat(Token::Comma) { break; }
                    }
                    self.eat(Token::RParen);
                    left = Expr::Call { callee: Box::new(left), args };
                }

                // Method call or property access: expr.method(args) 
                Token::Dot => {
                    self.advance();
                    if let Some(method_name) = self.eat_ident() {
                        if self.current_token == Token::LParen {
                            // Method call
                            self.advance();
                            let mut args = Vec::new();
                            while self.current_token != Token::RParen && self.current_token != Token::EOF {
                                args.push(self.parse_expression());
                                if !self.eat(Token::Comma) { break; }
                            }
                            self.eat(Token::RParen);
                            left = Expr::MethodCall {
                                callee: Box::new(left),
                                method: method_name,
                                args,
                            };
                        } else {
                            // Property access — treat as method call with no args
                            left = Expr::MethodCall {
                                callee: Box::new(left),
                                method: method_name,
                                args: vec![],
                            };
                        }
                    }
                }

                // Pipe operator: expr |> func
                Token::Pipe => {
                    self.advance();
                    let func = self.parse_primary();
                    left = Expr::Pipe {
                        input: Box::new(left),
                        function_call: Box::new(func),
                    };
                }

                // Binary operators
                _ if self.is_binary_op() => {
                    let op = self.get_binary_op_string();
                    self.advance();
                    let right = self.parse_expression();
                    // Tensor ops (.* .+)
                    if op == ".*" || op == ".+" {
                        left = Expr::TensorOp {
                            op,
                            left: Box::new(left),
                            right: Box::new(right),
                        };
                    } else {
                        left = Expr::BinaryOp {
                            op,
                            left: Box::new(left),
                            right: Box::new(right),
                        };
                    }
                }

                // Index access: expr[index]
                Token::LBracket => {
                    self.advance();
                    let index = self.parse_expression();
                    self.eat(Token::RBracket);
                    left = Expr::IndexAccess {
                        object: Box::new(left),
                        index: Box::new(index),
                    };
                }
                // Range operator: expr..expr
                Token::DotDot => {
                    self.advance();
                    let end = self.parse_primary();
                    left = Expr::Range {
                        start: Box::new(left),
                        end: Box::new(end),
                    };
                }
                
                // Ternary: condition ? then : else
                // OR Monadic: expr?
                Token::Question => {
                    self.advance(); // eat ?
                    
                    match &self.current_token {
                        Token::Semicolon | Token::RParen | Token::RBracket | Token::RBrace | Token::Comma | Token::Dot => {
                            left = Expr::Try(Box::new(left));
                        }
                        _ if self.is_binary_op() => {
                            left = Expr::Try(Box::new(left));
                        }
                        _ => {
                            // Ternary assumption
                            let then_expr = self.parse_expression();
                            self.eat(Token::Colon);
                            let else_expr = self.parse_expression();
                            left = Expr::Ternary {
                                condition: Box::new(left),
                                then_expr: Box::new(then_expr),
                                else_expr: Box::new(else_expr),
                            };
                        }
                    }
                }

                _ => break,
            }
        }

        left
    }

    fn is_binary_op(&self) -> bool {
        matches!(self.current_token,
            Token::Plus | Token::Minus | Token::Star | Token::Slash |
            Token::EqEq | Token::BangEq | Token::Lt | Token::Gt |
            Token::LtEq | Token::GtEq |
            Token::DotStar | Token::DotPlus |
            Token::And | Token::Or | Token::Percent
        )
    }

    fn get_binary_op_string(&self) -> String {
        match &self.current_token {
            Token::Plus    => "+".to_string(),
            Token::Minus   => "-".to_string(),
            Token::Star    => "*".to_string(),
            Token::Slash   => "/".to_string(),
            Token::EqEq    => "==".to_string(),
            Token::BangEq  => "!=".to_string(),
            Token::Lt      => "<".to_string(),
            Token::Gt      => ">".to_string(),
            Token::LtEq    => "<=".to_string(),
            Token::GtEq    => ">=".to_string(),
            Token::DotStar => ".*".to_string(),
            Token::DotPlus => ".+".to_string(),
            Token::And     => "&&".to_string(),
            Token::Or      => "||".to_string(),
            Token::Percent => "%".to_string(),
            _ => "?".to_string(),
        }
    }

    fn parse_primary(&mut self) -> Expr {
        match &self.current_token {
            Token::IntLit(v) => { let v=*v; self.advance(); Expr::LiteralInt(v) },
            Token::FloatLit(v) => { let v=*v; self.advance(); Expr::LiteralFloat(v) },
            Token::StringLit(s) => { let s=s.clone(); self.advance(); Expr::LiteralString(s) },
            Token::BoolLit(b) => { let b=*b; self.advance(); Expr::LiteralBool(b) },
            Token::Ident(s) => { 
                let s = s.clone(); 
                self.advance();
                // Macro call: name!(args)
                if self.current_token == Token::Bang {
                    self.advance();
                    self.eat(Token::LParen);
                    let mut args = Vec::new();
                    while self.current_token != Token::RParen && self.current_token != Token::EOF {
                        args.push(self.parse_expression());
                        if !self.eat(Token::Comma) { break; }
                    }
                    self.eat(Token::RParen);
                    return Expr::MacroCall { name: s, args };
                }
                Expr::Identifier(s) 
            },
            Token::New => {
                self.advance(); // eat 'new'
                if let Some(class_name) = self.eat_ident() {
                    self.eat(Token::LParen);
                    let mut args = Vec::new();
                    while self.current_token != Token::RParen && self.current_token != Token::EOF {
                        args.push(self.parse_expression());
                        if !self.eat(Token::Comma) { break; }
                    }
                    self.eat(Token::RParen);
                    Expr::New { class_name, args }
                } else {
                    Expr::Identifier("undefined".into())
                }
            },
            Token::Typeof => {
                self.advance(); // eat typeof
                Expr::Typeof(Box::new(self.parse_primary()))
            },
            Token::DotDotDot => {
                self.advance(); // eat ...
                Expr::Spread(Box::new(self.parse_primary()))
            },
            Token::Try => {
                self.advance(); // eat try
                Expr::Try(Box::new(self.parse_expression()))
            },
            Token::Await => {
                self.advance();
                let inner = self.parse_expression();
                Expr::Await(Box::new(inner))
            },
            // do |params| { body } — Ruby Block Closure
            Token::Do => {
                self.advance();
                let params = Vec::new();
                // |param1, param2|
                if self.current_token == Token::Ident("|".to_string()) || self.current_token == Token::Pipe {
                    // Note: our Pipe token is |>, we use a simulated approach
                }
                // Fallback: just parse the block
                let body = self.parse_block();
                Expr::BlockClosure { params, body }
            },
            Token::UnsafeZone => {
                self.advance();
                if let Token::StringLit(_) = self.current_token {
                    self.advance(); // skip the zone name
                }
                self.eat(Token::LBrace);
                let mut blk = vec![];
                while self.current_token != Token::RBrace && self.current_token != Token::EOF {
                    if let Some(s) = self.parse_statement() { blk.push(s); } else { self.advance(); }
                }
                self.eat(Token::RBrace);
                Expr::UnsafeBlock(blk)
            },
            Token::Query => {
                self.advance();
                self.eat(Token::LBrace);
                let mut query_body = String::new();
                while self.current_token != Token::RBrace && self.current_token != Token::EOF {
                    query_body.push_str(&format!("{:?} ", self.current_token));
                    self.advance();
                }
                self.eat(Token::RBrace);
                Expr::GraphQuery(query_body)
            },
            // Parenthesized expression OR Lambda: (expr) or (a, b) => expr
            Token::LParen => {
                // Save state: we need lookahead to detect lambda vs grouping
                // Strategy: parse param-like tokens, check for => after )
                self.advance(); // skip (
                
                // Quick check: is RParen immediately? That means () => ...
                if self.current_token == Token::RParen {
                    self.advance(); // skip )
                    if self.current_token == Token::FatArrow {
                        self.advance(); // skip =>
                        return self.parse_lambda_body(vec![]);
                    }
                    // Otherwise it's an empty grouping (unlikely, but safe)
                    return Expr::Identifier("undefined".into());
                }
                
                // Try to detect lambda: collect identifiers separated by commas
                // If we see : or non-ident, it's not a simple lambda param list
                let mut maybe_params: Vec<String> = Vec::new();
                let mut first_expr: Option<Expr> = None;
                
                // Peek: check if first token is an Ident
                if let Token::Ident(s) = self.current_token.clone() {
                    maybe_params.push(s);
                    self.advance();
                    
                    // After first ident, check for comma (more params) or RParen
                    match &self.current_token {
                        Token::Comma => {
                            self.advance();
                            // Continue collecting params
                            while let Token::Ident(p) = self.current_token.clone() {
                                maybe_params.push(p);
                                self.advance();
                                if !self.eat(Token::Comma) { break; }
                            }
                            if self.current_token == Token::RParen {
                                self.advance(); // skip )
                                if self.current_token == Token::FatArrow {
                                    self.advance();
                                    return self.parse_lambda_body(maybe_params);
                                }
                                // Not a lambda — can’t really recover cleanly, 
                                // treat first param as identifier
                            } else {
                                // Not a lambda closure
                            }
                        }
                        Token::RParen => {
                            self.advance(); // skip )
                            if self.current_token == Token::FatArrow {
                                self.advance();
                                return self.parse_lambda_body(maybe_params);
                            }
                            // It was (ident) — a grouped identifier
                            return Expr::Identifier(maybe_params.remove(0));
                        }
                        _ => {
                            // It’s (ident op ...) — a grouped expression
                            // Re-wrap the ident as an expression and continue parsing
                            let ident_expr = Expr::Identifier(maybe_params.remove(0));
                            first_expr = Some(ident_expr);
                        }
                    }
                }
                
                // Parse as parenthesized expression
                let inner = if let Some(expr) = first_expr {
                    self.continue_expression(expr)
                } else {
                    self.parse_expression()
                };
                self.eat(Token::RParen);
                inner
            },
            // Array literal: [expr, expr, ...]
            Token::LBracket => {
                self.advance();
                let mut elements = Vec::new();
                while self.current_token != Token::RBracket && self.current_token != Token::EOF {
                    elements.push(self.parse_expression());
                    if !self.eat(Token::Comma) { break; }
                }
                self.eat(Token::RBracket);
                Expr::ArrayLiteral(elements)
            },
            // Object literal in expression context: { key: val, ... }
            // Disambiguated from blocks because parse_primary is only called
            // from expression contexts (let x = {...}, fn args, etc.)
            Token::LBrace => {
                self.advance();
                let mut entries: Vec<(String, Expr)> = Vec::new();
                while self.current_token != Token::RBrace && self.current_token != Token::EOF {
                    if let Some(key) = self.eat_ident() {
                        self.eat(Token::Colon);
                        let value = self.parse_expression();
                        entries.push((key, value));
                        if !self.eat(Token::Comma) { break; }
                    } else if let Token::StringLit(key) = self.current_token.clone() {
                        self.advance();
                        self.eat(Token::Colon);
                        let value = self.parse_expression();
                        entries.push((key, value));
                        if !self.eat(Token::Comma) { break; }
                    } else {
                        break;
                    }
                }
                self.eat(Token::RBrace);
                Expr::ObjectLiteral(entries)
            },
            // Template literal: `hello ${name}!`
            Token::TemplateLiteral(segments) => {
                let segments = segments.clone();
                self.advance();
                let mut ast_segments = Vec::new();
                for (is_expr, content) in segments {
                    if is_expr {
                        // Re-parse the interpolated expression
                        let lexer = Lexer::new(&content);
                        let mut sub_parser = Parser::new(lexer);
                        let expr = sub_parser.parse_expression();
                        ast_segments.push(TemplateSegment::Interpolation(expr));
                    } else {
                        ast_segments.push(TemplateSegment::Str(content));
                    }
                }
                Expr::TemplateLiteral(ast_segments)
            },
            // Unary negative: -expr
            Token::Minus => {
                self.advance();
                let expr = self.parse_primary();
                Expr::Negative(Box::new(expr))
            },
            // Logical NOT: !expr (when not a macro call)
            Token::Bang => {
                self.advance();
                let expr = self.parse_primary();
                Expr::Not(Box::new(expr))
            },
            // Match expression: match subject { pattern => result, ... }
            Token::Match => {
                self.advance();
                let subject = self.parse_expression();
                self.eat(Token::LBrace);
                let mut arms = Vec::new();
                while self.current_token != Token::RBrace && self.current_token != Token::EOF {
                    let pattern = self.parse_primary(); // pattern is a primary expr (literal, ident, _)
                    self.eat(Token::FatArrow);
                    let body = self.parse_expression();
                    arms.push(MatchArm { pattern, body });
                    if !self.eat(Token::Comma) { break; }
                }
                self.eat(Token::RBrace);
                Expr::Match { subject: Box::new(subject), arms }
            },
            _ => { 
                eprintln!("⚠️  [PARSER] Token tidak dikenali dalam ekspresi: {:?}", self.current_token);
                self.advance(); 
                Expr::Identifier("undefined".into()) 
            }
        }
    }

    /// Parse lambda body: either a single expression or a block
    fn parse_lambda_body(&mut self, params: Vec<String>) -> Expr {
        if self.current_token == Token::LBrace {
            let body = self.parse_block();
            Expr::Lambda { params, body: LambdaBody::Block(body) }
        } else {
            let expr = self.parse_expression();
            Expr::Lambda { params, body: LambdaBody::Expr(Box::new(expr)) }
        }
    }

    /// Continue parsing an expression when we already have the left operand
    /// (used when lambda detection fails and we need to recover)
    fn continue_expression(&mut self, left: Expr) -> Expr {
        let mut left = left;
        loop {
            match &self.current_token {
                Token::LParen => {
                    self.advance();
                    let mut args = Vec::new();
                    while self.current_token != Token::RParen && self.current_token != Token::EOF {
                        args.push(self.parse_expression());
                        if !self.eat(Token::Comma) { break; }
                    }
                    self.eat(Token::RParen);
                    left = Expr::Call { callee: Box::new(left), args };
                }
                Token::Dot => {
                    self.advance();
                    if let Some(method_name) = self.eat_ident() {
                        if self.current_token == Token::LParen {
                            self.advance();
                            let mut args = Vec::new();
                            while self.current_token != Token::RParen && self.current_token != Token::EOF {
                                args.push(self.parse_expression());
                                if !self.eat(Token::Comma) { break; }
                            }
                            self.eat(Token::RParen);
                            left = Expr::MethodCall { callee: Box::new(left), method: method_name, args };
                        } else {
                            left = Expr::MethodCall { callee: Box::new(left), method: method_name, args: vec![] };
                        }
                    }
                }
                Token::LBracket => {
                    self.advance();
                    let index = self.parse_expression();
                    self.eat(Token::RBracket);
                    left = Expr::IndexAccess { object: Box::new(left), index: Box::new(index) };
                }
                _ if self.is_binary_op() => {
                    let op = self.get_binary_op_string();
                    self.advance();
                    let right = self.parse_expression();
                    left = Expr::BinaryOp { op, left: Box::new(left), right: Box::new(right) };
                }
                _ => break,
            }
        }
        left
    }
}
