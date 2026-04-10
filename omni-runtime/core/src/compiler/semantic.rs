use std::collections::HashMap;
use crate::compiler::ast::{OmniProgram, Stmt, Expr, Type};

#[derive(Debug, Clone)]
pub struct SemanticError {
    pub message: String,
}

impl std::fmt::Display for SemanticError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Semantic Error: {}", self.message)
    }
}

pub struct SymbolTable {
    // A stack of scopes. Global is scope 0.
    scopes: Vec<HashMap<String, Option<Type>>>,
    // Store types and existence of functions
    functions: HashMap<String, Option<Type>>,
}

impl SymbolTable {
    pub fn new() -> Self {
        Self {
            scopes: vec![HashMap::new()], // Global scope
            functions: HashMap::new(),
        }
    }

    pub fn enter_scope(&mut self) {
        self.scopes.push(HashMap::new());
    }

    pub fn leave_scope(&mut self) {
        self.scopes.pop();
    }

    pub fn declare_var(&mut self, name: &str, ty: Option<Type>) {
        if let Some(scope) = self.scopes.last_mut() {
            scope.insert(name.to_string(), ty);
        }
    }

    pub fn declare_function(&mut self, name: &str, return_ty: Option<Type>) {
        self.functions.insert(name.to_string(), return_ty.clone());
        // Also add to global scope as a variable reference
        if let Some(scope) = self.scopes.first_mut() {
            scope.insert(name.to_string(), return_ty);
        }
    }

    pub fn resolve(&self, name: &str) -> Option<Option<Type>> {
        // Build-ins
        if name == "println" || name == "print" || name == "OmniRuntime" {
            return Some(None);
        }

        // Search from innermost to global
        for scope in self.scopes.iter().rev() {
            if let Some(ty) = scope.get(name) {
                return Some(ty.clone());
            }
        }
        None
    }
}

pub struct SemanticAnalyzer {
    symbols: SymbolTable,
    errors: Vec<SemanticError>,
    in_unsafe_zone: bool,
}

impl SemanticAnalyzer {
    pub fn new() -> Self {
        Self {
            symbols: SymbolTable::new(),
            errors: Vec::new(),
            in_unsafe_zone: false,
        }
    }

    pub fn analyze(&mut self, program: &OmniProgram) -> Result<(), Vec<SemanticError>> {
        // Pass 1: Global declarations map
        self.pass1_globals(program);

        // Pass 2: Check resolution recursively
        for stmt in &program.statements {
            self.visit_stmt(stmt);
        }

        if self.errors.is_empty() {
            Ok(())
        } else {
            Err(self.errors.clone())
        }
    }

    fn pass1_globals(&mut self, program: &OmniProgram) {
        for stmt in &program.statements {
            match stmt {
                Stmt::FunctionDef { name, return_ty, .. } => {
                    self.symbols.declare_function(name, Some(return_ty.clone()));
                }
                Stmt::ConstDecl { id, ty, .. } => {
                    self.symbols.declare_var(id, Some(ty.clone()));
                }
                Stmt::LetDecl { id, ty, .. } => {
                    self.symbols.declare_var(id, ty.clone());
                }
                Stmt::StructDef { name, .. } | Stmt::TraitDef { name, .. } | Stmt::EnumDef { name, .. } => {
                    self.symbols.declare_var(name, None);
                }
                Stmt::ViewDef { name, .. } => {
                    self.symbols.declare_var(name, None);
                }
                Stmt::ImplDef { .. } => {
                    // Method bindings are structural and don't introduce global function names
                }
                Stmt::Assign { .. } | Stmt::CompoundAssign { .. } => {
                     // Wait, 'let' statements in top-level?
                     // Currently Stmt::ExprStmt(Expr::Let(...))
                }
                Stmt::ExprStmt(_) => {
                    // Locals handled in pass 2, globals don't leak from loose expressions
                }
                Stmt::ArrayDestructure { names, .. } => {
                    for n in names {
                        self.symbols.declare_var(n, None);
                    }
                }
                Stmt::Import { symbols, .. } => {
                    for (sym, alias) in symbols {
                        if let Some(a) = alias {
                            self.symbols.declare_var(a, None);
                        } else {
                            self.symbols.declare_var(sym, None);
                        }
                    }
                }
                _ => {} // Other top-level things
            }
        }
    }

    fn visit_stmt(&mut self, stmt: &Stmt) {
        match stmt {
            Stmt::ExprStmt(expr) => {
                self.visit_expr(expr);
            }
            Stmt::ConstDecl { id, ty, expr, .. } => {
                self.visit_expr(expr);
                self.symbols.declare_var(id, Some(ty.clone()));
            }
            Stmt::LetDecl { id, ty, expr, .. } => {
                self.visit_expr(expr);
                self.symbols.declare_var(id, ty.clone());
            }
            Stmt::FunctionDef { params, body, .. } => {
                self.symbols.enter_scope();
                for (param_name, param_ty) in params {
                    self.symbols.declare_var(param_name, Some(param_ty.clone()));
                }
                for b_stmt in body {
                    self.visit_stmt(b_stmt);
                }
                self.symbols.leave_scope();
            }
            Stmt::If { condition, then_branch, else_branch } => {
                self.visit_expr(condition);
                self.symbols.enter_scope();
                for s in then_branch {
                    self.visit_stmt(s);
                }
                self.symbols.leave_scope();

                if let Some(else_stmts) = else_branch {
                    self.symbols.enter_scope();
                    for s in else_stmts {
                        self.visit_stmt(s);
                    }
                    self.symbols.leave_scope();
                }
            }
            Stmt::While { condition, body } => {
                self.visit_expr(condition);
                self.symbols.enter_scope();
                for s in body {
                    self.visit_stmt(s);
                }
                self.symbols.leave_scope();
            }
            Stmt::ForIn { iterator, iterable, body } => {
                self.visit_expr(iterable);
                self.symbols.enter_scope();
                self.symbols.declare_var(iterator, None);
                for s in body {
                    self.visit_stmt(s);
                }
                self.symbols.leave_scope();
            }
            Stmt::Assign { target, value } | Stmt::CompoundAssign { target, value, .. } => {
                match self.symbols.resolve(target) {
                    Some(Some(target_ty)) => {
                        let val_ty = self.visit_expr(value);
                        if let Some(vt) = val_ty {
                            if target_ty != vt {
                                self.errors.push(SemanticError {
                                    message: format!("Type mismatch: cannot assign value of type {:?} to variable '{}' of type {:?}", vt, target, target_ty),
                                });
                            }
                        }
                    }
                    Some(None) => {
                        self.visit_expr(value);
                    }
                    None => {
                        self.errors.push(SemanticError { message: format!("Undeclared variable '{}' in assignment.", target) });
                        self.visit_expr(value);
                    }
                }
            }
            Stmt::ArrayDestructure { names, expr } => {
                self.visit_expr(expr);
                for n in names {
                    self.symbols.declare_var(n, None);
                }
            }
            Stmt::Spawn(expr) => {
                self.visit_expr(expr);
            }
            Stmt::TraitDef { .. } | Stmt::EnumDef { .. } | Stmt::StructDef { .. } | Stmt::ViewDef { .. } | Stmt::Import { .. } | Stmt::Export { .. } => {
                // Handled in pass 1
            }
            Stmt::ImplDef { methods, .. } => {
                for m in methods {
                    if let Stmt::FunctionDef { params, body, .. } = m {
                        self.symbols.enter_scope();
                        self.symbols.declare_var("self", None); // Inject 'self'
                        for (param_name, param_ty) in params {
                            self.symbols.declare_var(param_name, Some(param_ty.clone()));
                        }
                        for b_stmt in body {
                            self.visit_stmt(b_stmt);
                        }
                        self.symbols.leave_scope();
                    }
                }
            }
            Stmt::UnsafeZone { body, .. } => {
                let prev = self.in_unsafe_zone;
                self.in_unsafe_zone = true;
                for s in body {
                    self.visit_stmt(s);
                }
                self.in_unsafe_zone = prev;
            }
            Stmt::PolyglotBlock { lang, .. } => {
                if self.in_unsafe_zone {
                    match lang.as_str() {
                        "c" | "cpp" | "rust" => {} // Safe
                        _ => {
                            self.errors.push(SemanticError {
                                message: format!("Domain Segregation Violation: Layer '{}' tidak diizinkan di dalam `unsafe_zone`. Hanya C, C++, dan Rust yang diperbolehkan.", lang)
                            });
                        }
                    }
                } else {
                    match lang.as_str() {
                        "c" | "cpp" | "rust" => {
                            self.errors.push(SemanticError {
                                message: format!("Domain Segregation Violation: Layer '{}' membutuhkan blok `unsafe_zone`.", lang)
                            });
                        }
                        _ => {}
                    }
                }
            }
            _ => {}
        }
    }

    fn visit_expr(&mut self, expr: &Expr) -> Option<Type> {
        match expr {
            Expr::LiteralInt(_) => Some(Type::Int),
            Expr::LiteralFloat(_) => Some(Type::Float),
            Expr::LiteralString(_) => Some(Type::String),
            Expr::LiteralBool(_) => Some(Type::Bool),
            Expr::Identifier(name) => {
                match self.symbols.resolve(name) {
                    Some(Some(ty)) => Some(ty),
                    Some(None) => None,
                    None => {
                        self.errors.push(SemanticError {
                            message: format!("Reference to undeclared identifier: '{}'", name)
                        });
                        None
                    }
                }
            }
            Expr::BinaryOp { left, right, .. } | Expr::TensorOp { left, right, .. } => {
                let l_ty = self.visit_expr(left);
                self.visit_expr(right);
                l_ty // Just a naive inference from left for now
            }
            Expr::Call { callee, args } => {
                self.visit_expr(callee);
                for a in args {
                    self.visit_expr(a);
                }
                None
            }
            Expr::MethodCall { callee, args, .. } => {
                self.visit_expr(callee);
                for a in args {
                    self.visit_expr(a);
                }
                None
            }
            Expr::IndexAccess { object, index } => {
                self.visit_expr(object);
                self.visit_expr(index);
                None
            }
            Expr::ArrayLiteral(arr) => {
                for i in arr {
                    self.visit_expr(i);
                }
                None // Could infer array element types theoretically
            }
            Expr::ObjectLiteral(fields) => {
                for (_, v) in fields {
                    self.visit_expr(v);
                }
                None
            }
            Expr::DynamicObject(fields) => {
                for (_, v) in fields {
                    self.visit_expr(v);
                }
                Some(Type::Dynamic)
            }
            Expr::Negative(operand) | Expr::Not(operand) => {
                self.visit_expr(operand)
            }
            Expr::Ternary { condition, then_expr, else_expr } => {
                self.visit_expr(condition);
                let ty = self.visit_expr(then_expr);
                self.visit_expr(else_expr);
                ty
            }
            Expr::Typeof(val) | Expr::Spread(val) | Expr::Try(val) => {
                self.visit_expr(val);
                None // Typeof returns string, Try might return Option/Result, but we use None for simplicity right now
            }
            Expr::Range { start, end } => {
                self.visit_expr(start);
                self.visit_expr(end);
                None
            }
            Expr::Lambda { params, body } => {
                self.symbols.enter_scope();
                for p in params {
                    self.symbols.declare_var(p, None);
                }
                let mut ret_ty = None;
                match body {
                    crate::compiler::ast::LambdaBody::Expr(e) => {
                        ret_ty = self.visit_expr(e);
                    }
                    crate::compiler::ast::LambdaBody::Block(stmts) => {
                        for s in stmts {
                            self.visit_stmt(s);
                        }
                    }
                }
                self.symbols.leave_scope();
                ret_ty // Or functional type Wrapper, but just return none or ret
            }
            Expr::TemplateLiteral(parts) => {
                for p in parts {
                    if let crate::compiler::ast::TemplateSegment::Interpolation(e) = p {
                        self.visit_expr(e);
                    }
                }
                Some(Type::String)
            }
            Expr::Match { subject, arms } => {
                self.visit_expr(subject);
                let mut first_ty = None;
                for arm in arms {
                    let t = self.visit_expr(&arm.body);
                    if first_ty.is_none() {
                        first_ty = t;
                    }
                }
                first_ty
            }
            Expr::New { class_name, args } => {
                for a in args {
                    self.visit_expr(a);
                }
                Some(Type::Struct(class_name.clone()))
            }
            _ => None,
        }
    }
}
