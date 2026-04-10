// AST untuk OMNI-PRIME The Realism Protocol
#[derive(Debug, PartialEq, Clone)]
pub struct Program {
    pub body: Vec<Statement>,
}

#[derive(Debug, PartialEq, Clone)]
pub enum Type {
    Int,
    String,
    Bool,
    Float,
    Optional(Box<Type>),
    Custom(String),
}

#[derive(Debug, PartialEq, Clone)]
pub struct StructDecl {
    pub name: String,
    pub fields: Vec<FieldDecl>,
}

#[derive(Debug, PartialEq, Clone)]
pub struct FieldDecl {
    pub name: String,
    pub field_type: Type,
    pub default_value: Option<Expr>,
}

#[derive(Debug, PartialEq, Clone)]
pub struct FnDecl {
    pub name: String,
    pub params: Vec<ParamDecl>,
    pub return_type: Option<Type>,
    pub body: Vec<Statement>,
}

#[derive(Debug, PartialEq, Clone)]
pub struct ParamDecl {
    pub name: String,
    pub param_type: Type,
}

#[derive(Debug, PartialEq, Clone)]
pub enum Statement {
    LetBinding { name: String, value: Expr },
    If { condition: Expr, body: Vec<Statement>, else_body: Option<Vec<Statement>> },
    Return(Expr),
    ExprStmt(Expr),
    FunctionDeclaration(FnDecl),
    UnsafeZone { name: String, body: Vec<Statement> },
}

#[derive(Debug, PartialEq, Clone)]
pub struct InjectedPointer {
    pub internal_name: String,
    pub references_to: String,
}

#[derive(Debug, PartialEq, Clone)]
pub struct PolyglotNode {
    pub language: String,
    pub source_code: String,
    pub injected_pointers: Vec<InjectedPointer>,
}

#[derive(Debug, PartialEq, Clone)]
pub enum Expr {
    IntLiteral(i64),
    NumberLiteral(f64),
    StringLiteral(String),
    BoolLiteral(bool),
    Identifier(String),
    Call { callee: Box<Expr>, args: Vec<Expr> },
    Await(Box<Expr>),
    Spawn(Box<Expr>),
    NullCoalesce { left: Box<Expr>, right: Box<Expr> },
    OptionalChain { left: Box<Expr>, field: String },
    DictionaryAccess { left: Box<Expr>, key: String },
    PolyglotNode(PolyglotNode),
}
