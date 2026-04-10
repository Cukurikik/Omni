#[derive(Debug, Clone, PartialEq)]
pub enum Type {
    // 1. Tipe data ketat (TS/Rust/Swift)
    Int,
    Float,
    String,
    Bool,
    Void,
    
    // Union & Generics
    Union(Vec<Type>),
    Generic(String, Vec<Type>),
    Struct(String),
    
    // 4. Konkurensi Channel
    Channel(Box<Type>),
    
    // 5. Tensor Mathematics
    Tensor(Box<Type>),
    
    // 11. Event-Driven Dynamic
    Dynamic,
    
    // Other Primitives
    UUID,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Expr {
    LiteralInt(i64),
    LiteralFloat(f64),
    LiteralString(String),
    LiteralBool(bool),
    Identifier(String),

    // 5. Vektor Tensor (Julia/Python/R)
    TensorOp {
        op: String, // e.g., ".*", ".+"
        left: Box<Expr>,
        right: Box<Expr>,
    },

    // 15. Native Graph Queries (GraphQL)
    GraphQuery(String), // For phase 1, we treat the content as a raw string to be evaluated

    // 7. Reaktivitas Antarmuka (HTML/TS/React)
    UINode {
        tag: String,
        props: std::collections::HashMap<String, Expr>,
        children: Vec<Expr>,
    },

    // 12. Data Piping (R)
    Pipe {
        input: Box<Expr>,
        function_call: Box<Expr>, // Specifically a chained Call tree
    },
    
    // 6. Bare-Metal Memory
    UnsafeBlock(Vec<Stmt>),
    
    // 8. Metaprogramming DSL (Ruby closure)
    BlockClosure {
        params: Vec<String>,
        body: Vec<Stmt>,
    },

    // 14. Compile-Time Macros
    MacroCall {
        name: String,
        args: Vec<Expr>, // Or raw token stream in a real compiler
    },
    
    Call {
        callee: Box<Expr>,
        args: Vec<Expr>,
    },
    
    MethodCall {
        callee: Box<Expr>,
        method: String,
        args: Vec<Expr>,
    },

    // 11. Dynamic Objects (JS)
    DynamicObject(std::collections::HashMap<String, Expr>),
    
    Await(Box<Expr>),
    
    BinaryOp {
        op: String,
        left: Box<Expr>,
        right: Box<Expr>,
    },

    // ── Phase 1: Language Essentials ──
    
    // Array literal: [1, 2, 3]
    ArrayLiteral(Vec<Expr>),
    
    // Object literal: { key: value, key2: value2 }
    ObjectLiteral(Vec<(String, Expr)>),
    
    // Lambda / Arrow function: (x, y) => x + y
    Lambda {
        params: Vec<String>,
        body: LambdaBody,
    },
    
    // Template literal: `hello ${name}!`
    TemplateLiteral(Vec<TemplateSegment>),
    
    // Index access: arr[0], obj["key"]
    IndexAccess {
        object: Box<Expr>,
        index: Box<Expr>,
    },
    
    // Unary negative: -expr
    Negative(Box<Expr>),

    // ── Phase 2: Advanced Control Flow ──
    
    // Match expression: match expr { pattern => result, ... }
    Match {
        subject: Box<Expr>,
        arms: Vec<MatchArm>,
    },
    
    // Range: start..end
    Range {
        start: Box<Expr>,
        end: Box<Expr>,
    },
    
    // Logical NOT: !expr
    Not(Box<Expr>),

    // ── Phase 3: Structs & Operators ──
    
    // Constructor: new StructName(args)
    New {
        class_name: String,
        args: Vec<Expr>,
    },
    
    // Ternary: condition ? then_expr : else_expr
    Ternary {
        condition: Box<Expr>,
        then_expr: Box<Expr>,
        else_expr: Box<Expr>,
    },
    
    // Spread: ...expr
    Spread(Box<Expr>),
    
    // Typeof: typeof expr
    Typeof(Box<Expr>),
    
    // ── Phase 4: Modules & Error Handling ──
    
    // Monadic Try: try expr or expr?
    Try(Box<Expr>),
}

/// Lambda body can be a single expression or a block of statements
#[derive(Debug, Clone, PartialEq)]
pub enum LambdaBody {
    Expr(Box<Expr>),
    Block(Vec<Stmt>),
}

/// Template literal segments: alternating string parts and expression interpolations
#[derive(Debug, Clone, PartialEq)]
pub enum TemplateSegment {
    Str(String),
    Interpolation(Expr),
}

/// Match arm: pattern => result_expression
#[derive(Debug, Clone, PartialEq)]
pub struct MatchArm {
    pub pattern: Expr,   // The pattern to match (literal, identifier "_" for wildcard)
    pub body: Expr,      // The result expression
}

#[derive(Debug, Clone, PartialEq)]
pub enum Stmt {
    // 1. Tipe data ketat (let mut)
    LetDecl {
        is_mut: bool,
        id: String,
        ty: Option<Type>,
        expr: Expr,
    },
    
    // Const (C/C++)
    ConstDecl {
        id: String,
        ty: Type,
        expr: Expr,
    },
    
    // 2. Fungsi aman (Monadic Result)
    FunctionDef {
        is_pub: bool,
        is_async: bool,
        name: String,
        params: Vec<(String, Type)>,
        return_ty: Type, 
        body: Vec<Stmt>,
    },

    // 7. UI / Frontend View Def
    ViewDef {
        is_export: bool,
        name: String,
        params: Vec<(String, Type)>,
        body: Vec<Stmt>, // Return an expression UINode
    },

    // 3. Skema Data (Decorators/Structs)
    StructDef {
        is_pub: bool,
        name: String,
        decorators: Vec<String>,
        fields: Vec<(String, Type, Vec<String>)>, // Field name, type, field decorators
    },

    // 10. Advanced OOP
    ClassDef {
        name: String,
        generics: Vec<String>,
        extends: Option<String>,
        implements: Vec<String>,
        methods: Vec<Stmt>, // Typically FunctionDefs inside
    },

    // 13. Protocol Extensions
    ExtensionDef {
        target_ty: String,
        methods: Vec<Stmt>,
    },

    // 4. Konkurensi (Go spawn)
    Spawn(Expr),

    ExprStmt(Expr),
    Return(Expr),
    Yield(Expr), // Yield blocks
    
    // 6. Cross-Language FFI Bridging (Phase 9)
    UnsafeZone {
        name: String,
        body: Vec<Stmt>,
    },
    
    // FFI Block
    PolyglotBlock {
        lang: String,
        body: Vec<Stmt>,
    },
    
    If {
        condition: Expr,
        then_branch: Vec<Stmt>,
        else_branch: Option<Vec<Stmt>>,
    },
    
    ForIn {
        iterator: String,
        iterable: Expr,
        body: Vec<Stmt>
    },

    // 16. Modul Sistem (Imports/Exports)
    Import {
        path: String,
        symbols: Vec<(String, Option<String>)>, // id as alias
    },
    Export {
        symbols: Vec<String>,
    },

    // ── Phase 2: Advanced Control Flow ──
    
    // While loop: while condition { ... }
    While {
        condition: Expr,
        body: Vec<Stmt>,
    },
    
    // Enum definition: enum Color { Red, Green, Blue }
    EnumDef {
        name: String,
        variants: Vec<String>,
    },
    
    // Mutable assignment: identifier = expr
    Assign {
        target: String,
        value: Expr,
    },
    
    // Break and Continue
    Break,
    Continue,

    // ── Phase 3: Structs & Operators ──
    
    // Compound assignment: x += 1, x -= 1, etc.
    CompoundAssign {
        target: String,
        op: String,  // "+=", "-=", "*=", "/="
        value: Expr,
    },
    
    // Array destructuring: let [a, b, c] = expr;
    ArrayDestructure {
        names: Vec<String>,
        expr: Expr,
    },

    // ── Phase 4: Traits ──
    TraitDef {
        name: String,
        methods: Vec<Stmt>, // Usually FunctionDef without body
    },
    
    // Impl definition: impl Name { ... } or impl Trait for Name { ... }
    ImplDef {
        target: String,
        trait_name: Option<String>,
        methods: Vec<Stmt>,
    },
}

#[derive(Debug, Clone, PartialEq)]
pub struct OmniProgram {
    pub statements: Vec<Stmt>,
}
