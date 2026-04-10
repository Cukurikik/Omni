use crate::compiler::ast::{OmniProgram, Stmt, Expr, LambdaBody, TemplateSegment};

/// OMNI Transpiler v2.0
/// Menerjemahkan seluruh 15 paradigm dari OMNI AST menjadi
/// V8/Node JavaScript Backend secara komprehensif.
pub struct OmniTranspiler {
    is_release: bool,
}

impl OmniTranspiler {
    pub fn new(is_release: bool) -> Self {
        OmniTranspiler { is_release }
    }

    pub fn transpile(&self, program: &OmniProgram) -> String {
        let mut js_code = String::new();
        if !self.is_release {
            js_code.push_str("// ═══ OMNI TRANSPILED OUTPUT ═══\n");
        }
        js_code.push_str("\"use strict\";");
        if !self.is_release { js_code.push('\n'); }
        
        for stmt in &program.statements {
            js_code.push_str(&self.transpile_stmt(stmt, 0));
            if !self.is_release { js_code.push('\n'); } else { js_code.push(' '); }
        }
        
        if !self.is_release { js_code.push_str("\n// Auto-invoke main if present\n"); }
        js_code.push_str("if (typeof main === 'function') { main(); }");
        if !self.is_release { js_code.push('\n'); }
        
        js_code
    }

    fn indent(&self, depth: usize) -> String {
        if self.is_release { return "".to_string(); }
        "  ".repeat(depth)
    }

    fn transpile_stmt(&self, stmt: &Stmt, depth: usize) -> String {
        let pad = self.indent(depth);
        match stmt {
            // ── Variabel (Rust/TypeScript style) ──
            Stmt::LetDecl { is_mut, id, ty: _, expr } => {
                let kw = if *is_mut { "let" } else { "const" };
                format!("{}{} {} = {};", pad, kw, id, self.transpile_expr(expr))
            }
            Stmt::ConstDecl { id, ty: _, expr } => {
                format!("{}const {} = {};", pad, id, self.transpile_expr(expr))
            }

            // ── Ekspresi biasa ──
            Stmt::ExprStmt(expr) => {
                format!("{}{};", pad, self.transpile_expr(expr))
            }

            // ── Go Spawn → Async Micro-task ──
            Stmt::Spawn(expr) => {
                format!("{}setTimeout(async () => {{ {} }}, 0);", pad, self.transpile_expr(expr))
            }

            // ── Fungsi (sync / async) ──
            Stmt::FunctionDef { is_pub, is_async, name, params, return_ty: _, body } => {
                let export_kw = if *is_pub { "export " } else { "" };
                let async_kw = if *is_async { "async " } else { "" };
                let param_list: Vec<String> = params.iter().map(|(n, _)| n.clone()).collect();
                let mut body_str = String::new();
                for b_stmt in body {
                    body_str.push_str(&self.transpile_stmt(b_stmt, depth + 1));
                    body_str.push('\n');
                }
                format!("{}{}{}function {}({}) {{\n{}{}}}", pad, export_kw, async_kw, name, param_list.join(", "), body_str, pad)
            }

            // ── Return ──
            Stmt::Return(expr) => {
                format!("{}return {};", pad, self.transpile_expr(expr))
            }

            // ── Yield (Generator) ──
            Stmt::Yield(expr) => {
                format!("{}yield {};", pad, self.transpile_expr(expr))
            }

            // ── Struct → JS Class ──
            Stmt::StructDef { is_pub: _, name, decorators: _, fields } => {
                let field_names: Vec<String> = fields.iter().map(|(n, _, _)| n.clone()).collect();
                let constructor_params = field_names.join(", ");
                let assignments: String = field_names.iter()
                    .map(|f| format!("{}  this.{} = {};", pad, f, f))
                    .collect::<Vec<_>>()
                    .join("\n");
                format!("{}class {} {{\n{}  constructor({}) {{\n{}\n{}  }}\n{}}}", 
                    pad, name, pad, constructor_params, assignments, pad, pad)
            }

            // ── Class → JS Class (extends/implements) ──
            Stmt::ClassDef { name, generics: _, extends, implements: _, methods } => {
                let extends_str = match extends {
                    Some(parent) => format!(" extends {}", parent),
                    None => String::new(),
                };
                let mut methods_str = String::new();
                for m in methods {
                    methods_str.push_str(&self.transpile_class_method(m, depth + 1));
                    methods_str.push('\n');
                }
                format!("{}class {}{} {{\n{}{}}}", pad, name, extends_str, methods_str, pad)
            }

            // ── View → Component Function ──
            Stmt::ViewDef { is_export: _, name, params, body } => {
                let param_list: Vec<String> = params.iter().map(|(n, _)| n.clone()).collect();
                let mut body_str = String::new();
                for b_stmt in body {
                    body_str.push_str(&self.transpile_stmt(b_stmt, depth + 1));
                    body_str.push('\n');
                }
                format!("{}function {}({}) {{\n{}{}}}", pad, name, param_list.join(", "), body_str, pad)
            }

            // ── Protocol Extension → Prototype Patch ──
            Stmt::ExtensionDef { target_ty, methods } => {
                let mut out = String::new();
                for m in methods {
                    if let Stmt::FunctionDef { name, params, body, .. } = m {
                        let param_list: Vec<String> = params.iter().map(|(n, _)| n.clone()).collect();
                        let mut body_str = String::new();
                        for b in body {
                            body_str.push_str(&self.transpile_stmt(b, depth + 1));
                            body_str.push('\n');
                        }
                        out.push_str(&format!("{}{}.prototype.{} = function({}) {{\n{}{}}}\n",
                            pad, target_ty, name, param_list.join(", "), body_str, pad));
                    }
                }
                out
            }

            // ── If / Else ──
            Stmt::If { condition, then_branch, else_branch } => {
                let mut s = format!("{}if ({}) {{\n", pad, self.transpile_expr(condition));
                for stmt in then_branch {
                    s.push_str(&self.transpile_stmt(stmt, depth + 1));
                    s.push('\n');
                }
                s.push_str(&format!("{}}}", pad));
                if let Some(else_stmts) = else_branch {
                    s.push_str(" else {\n");
                    for stmt in else_stmts {
                        s.push_str(&self.transpile_stmt(stmt, depth + 1));
                        s.push('\n');
                    }
                    s.push_str(&format!("{}}}", pad));
                }
                s
            }

            // ── For-In Loop ──
            Stmt::ForIn { iterator, iterable, body } => {
                let mut body_str = String::new();
                for b in body {
                    body_str.push_str(&self.transpile_stmt(b, depth + 1));
                    body_str.push('\n');
                }
                format!("{}for (const {} of {}) {{\n{}{}}}", pad, iterator, self.transpile_expr(iterable), body_str, pad)
            }

            // ── Import (ESM Style) ──
            // ── Import (ESM Style) ──
            Stmt::Import { path, symbols } => {
                let out = if symbols.is_empty() {
                    format!("{}// import \"./{}\"; (bundled)", pad, path)
                } else {
                    let parts: Vec<String> = symbols.iter().map(|(id, alias)| {
                        match alias {
                            Some(a) => format!("{} as {}", id, a),
                            None => id.clone()
                        }
                    }).collect();
                    format!("{}// import {{ {} }} from \"./{}\"; (bundled)", pad, parts.join(", "), path)
                };
                out
            }

            // ── Export ──
            Stmt::Export { symbols } => {
                format!("{}// export {{ {} }}; (bundled)", pad, symbols.join(", "))
            }

            // ── Phase 2: Advanced Control Flow ──

            // While loop
            Stmt::While { condition, body } => {
                let mut body_str = String::new();
                for b in body {
                    body_str.push_str(&self.transpile_stmt(b, depth + 1));
                    body_str.push('\n');
                }
                format!("{}while ({}) {{\n{}{}}}", pad, self.transpile_expr(condition), body_str, pad)
            }

            // Enum → Frozen Object
            Stmt::EnumDef { name, variants } => {
                let entries: Vec<String> = variants.iter()
                    .map(|v| format!("  {}: \"{}\"", v, v))
                    .collect();
                format!("{}const {} = Object.freeze({{\n{}\n{}}});", pad, name, entries.join(",\n"), pad)
            }

            // Break / Continue
            Stmt::Break => format!("{}break;", pad),
            Stmt::Continue => format!("{}continue;", pad),

            // Mutable Assignment
            Stmt::Assign { target, value } => {
                format!("{}{} = {};", pad, target, self.transpile_expr(value))
            }
            
            // Compound Assignment (x += 1)
            Stmt::CompoundAssign { target, op, value } => {
                format!("{}{} {} {};", pad, target, op, self.transpile_expr(value))
            }
            
            // Array Destructuring (let [a, b] = arr)
            Stmt::ArrayDestructure { names, expr } => {
                let vars = names.join(", ");
                format!("{}let [{}] = {};", pad, vars, self.transpile_expr(expr))
            }

            // ── Phase 4: Traits ──
            Stmt::TraitDef { name, .. } => {
                // In JavaScript, traits don't exist natively. We can emit a comment 
                // and a Symbol to simulate a structural interface token if needed,
                // or just declare an empty object/Symbol representing the Trait type.
                let mut out = format!("{}// Trait {}\n", pad, name);
                out.push_str(&format!("{}const {} = Symbol(\"Trait:{}\");", pad, name, name));
                out
            }

            // ── Phase 6: ImplDef → Prototype Extension ──
            Stmt::ImplDef { target, trait_name: _, methods } => {
                let mut out = String::new();
                for m in methods {
                    if let Stmt::FunctionDef { name, params, body, .. } = m {
                        // Normally in Rust-like systems `self` is the first parameter.
                        // Here JS `this` acts as `self`. If `self` is explicitly passed in OMNI,
                        // we can either map it or allow JS `this` scoping. For pure JS transparency,
                        // we'll filter out `self` from JS params because it uses `this` implicitly.
                        let param_list: Vec<String> = params.iter()
                            .filter(|(n, _)| n != "self")
                            .map(|(n, _)| n.clone())
                            .collect();
                            
                        let mut body_str = String::new();
                        body_str.push_str(&format!("{}  const self = this;\n", pad));
                        for b in body {
                            body_str.push_str(&self.transpile_stmt(b, depth + 1));
                            body_str.push('\n');
                        }
                        out.push_str(&format!("{}{}.prototype.{} = function({}) {{\n{}{}}};\n",
                            pad, target, name, param_list.join(", "), body_str, pad));
                    }
                }
                out
            }

            // ── Phase 9: Unsafe Zone FFI Boundary ──
            Stmt::UnsafeZone { name, body } => {
                let mut body_str = String::new();
                body_str.push_str(&format!("{}// ⚡ OMNI FFI BOUNDARY: {:?}\n", pad, name));
                for b in body {
                    body_str.push_str(&self.transpile_stmt(b, depth + 1));
                    body_str.push('\n');
                }
                format!("{}{{{{\n{}{}}}}}", pad, body_str, pad)
            }
            
            Stmt::PolyglotBlock { lang, body } => {
                let mut body_str = String::new();
                for b in body {
                    body_str.push_str(&self.transpile_stmt(b, depth + 1));
                    body_str.push('\n');
                }
                // Convert polyglot block to a native bridge call
                format!("{}__omni_ffi(\"{}\", `\n{}{}`);", pad, lang, body_str, pad)
            }
        }
    }

    fn transpile_expr(&self, expr: &Expr) -> String {
        match expr {
            Expr::LiteralInt(val) => val.to_string(),
            Expr::LiteralFloat(val) => val.to_string(),
            Expr::LiteralString(val) => format!("\"{}\"", val),
            Expr::LiteralBool(val) => val.to_string(),
            Expr::Identifier(ident) => ident.clone(),

            Expr::BinaryOp { op, left, right } => {
                format!("({} {} {})", self.transpile_expr(left), op, self.transpile_expr(right))
            }
            Expr::Call { callee, args } => {
                let args_str: Vec<String> = args.iter().map(|a| self.transpile_expr(a)).collect();
                format!("{}({})", self.transpile_expr(callee), args_str.join(", "))
            }
            Expr::MethodCall { callee, method, args } => {
                if args.is_empty() {
                    // Property access: obj.prop (no parentheses)
                    format!("{}.{}", self.transpile_expr(callee), method)
                } else {
                    let args_str: Vec<String> = args.iter().map(|a| self.transpile_expr(a)).collect();
                    format!("{}.{}({})", self.transpile_expr(callee), method, args_str.join(", "))
                }
            }
            Expr::Await(inner) => {
                format!("(await {})", self.transpile_expr(inner))
            }
            
            Expr::New { class_name, args } => {
                let args_str: Vec<String> = args.iter().map(|a| self.transpile_expr(a)).collect();
                format!("new {}({})", class_name, args_str.join(", "))
            }
            Expr::Spread(inner) => {
                format!("...{}", self.transpile_expr(inner))
            }
            Expr::Typeof(inner) => {
                format!("(typeof {})", self.transpile_expr(inner))
            }
            Expr::Ternary { condition, then_expr, else_expr } => {
                format!("({} ? {} : {})", 
                    self.transpile_expr(condition),
                    self.transpile_expr(then_expr),
                    self.transpile_expr(else_expr)
                )
            }
            
            Expr::Try(inner) => {
                // To support monadic `expr?` unwrapping via OMNI Runtime
                format!("OmniRuntime.unwrap({})", self.transpile_expr(inner))
            }

            // ── Julia/Python Tensor → WASM Math ──
            Expr::TensorOp { op, left, right } => {
                format!("OmniMath.tensorOp(\"{}\", {}, {})", op, self.transpile_expr(left), self.transpile_expr(right))
            }

            // ── Unsafe Block → IIFE ──
            Expr::UnsafeBlock(stmts) => {
                let mut body = String::new();
                for s in stmts {
                    body.push_str(&self.transpile_stmt(s, 1));
                    body.push('\n');
                }
                format!("(() => {{\n{}}})() /* unsafe */", body)
            }

            // ── GraphQL Query → Tagged Template ──
            Expr::GraphQuery(query) => {
                format!("OmniGraph.query(`{}`)", query)
            }

            // ── Ruby Block Closure → Arrow Function ──
            Expr::BlockClosure { params, body } => {
                let params_str = params.join(", ");
                let mut body_str = String::new();
                for s in body {
                    body_str.push_str(&self.transpile_stmt(s, 1));
                    body_str.push('\n');
                }
                format!("({}) => {{\n{}}}", params_str, body_str)
            }

            // ── Dynamic Object (JS) ──
            Expr::DynamicObject(map) => {
                let entries: Vec<String> = map.iter()
                    .map(|(k, v)| format!("{}: {}", k, self.transpile_expr(v)))
                    .collect();
                format!("{{ {} }}", entries.join(", "))
            }

            // ── R-style Pipe → Chained Call ──
            Expr::Pipe { input, function_call } => {
                // input |> fn(x) → fn(input)
                format!("{}({})", self.transpile_expr(function_call), self.transpile_expr(input))
            }

            // ── Compile-Time Macro → Comment Annotation ──
            Expr::MacroCall { name, args } => {
                let args_str: Vec<String> = args.iter().map(|a| self.transpile_expr(a)).collect();
                format!("/* @{} */ {}({})", name, name, args_str.join(", "))
            }

            // ── UI JSX Node → createElement ──
            Expr::UINode { tag, props, children } => {
                let props_str: Vec<String> = props.iter()
                    .map(|(k, v)| format!("{}: {}", k, self.transpile_expr(v)))
                    .collect();
                let children_str: Vec<String> = children.iter()
                    .map(|c| self.transpile_expr(c))
                    .collect();
                format!("OmniUI.createElement(\"{}\", {{ {} }}, [{}])", 
                    tag, props_str.join(", "), children_str.join(", "))
            }

            // ── Phase 1: Language Essentials ──
            
            // Array literal: [1, 2, 3]
            Expr::ArrayLiteral(elements) => {
                let elems: Vec<String> = elements.iter().map(|e| self.transpile_expr(e)).collect();
                format!("[{}]", elems.join(", "))
            }
            
            // Object literal: { key: value }
            Expr::ObjectLiteral(entries) => {
                let pairs: Vec<String> = entries.iter()
                    .map(|(k, v)| format!("{}: {}", k, self.transpile_expr(v)))
                    .collect();
                format!("({{ {} }})", pairs.join(", "))
            }
            
            // Lambda: (x, y) => x + y
            Expr::Lambda { params, body } => {
                let params_str = params.join(", ");
                match body {
                    LambdaBody::Expr(expr) => {
                        format!("({}) => {}", params_str, self.transpile_expr(expr))
                    }
                    LambdaBody::Block(stmts) => {
                        let mut body_str = String::new();
                        for s in stmts {
                            body_str.push_str(&self.transpile_stmt(s, 1));
                            body_str.push('\n');
                        }
                        format!("({}) => {{\n{}}}", params_str, body_str)
                    }
                }
            }
            
            // Template literal: `hello ${name}!`
            Expr::TemplateLiteral(segments) => {
                let mut parts = String::from("`");
                for seg in segments {
                    match seg {
                        TemplateSegment::Str(s) => parts.push_str(s),
                        TemplateSegment::Interpolation(expr) => {
                            parts.push_str("${");
                            parts.push_str(&self.transpile_expr(expr));
                            parts.push('}');
                        }
                    }
                }
                parts.push('`');
                parts
            }
            
            // Index access: arr[0]
            Expr::IndexAccess { object, index } => {
                format!("{}[{}]", self.transpile_expr(object), self.transpile_expr(index))
            }
            
            // Unary negative: -expr
            Expr::Negative(expr) => {
                format!("(-{})", self.transpile_expr(expr))
            }

            // ── Phase 2: Advanced Control Flow ──

            // Match → if/else chain
            Expr::Match { subject, arms } => {
                let subject_js = self.transpile_expr(subject);
                let mut out = String::from("(() => { const __m = ");
                out.push_str(&subject_js);
                out.push_str("; ");
                let mut first = true;
                for arm in arms {
                    // Check if pattern is wildcard (_) 
                    let is_wildcard = matches!(&arm.pattern, Expr::Identifier(s) if s == "_");
                    if is_wildcard {
                        out.push_str(&format!("return {}; ", self.transpile_expr(&arm.body)));
                    } else {
                        let pattern_js = self.transpile_expr(&arm.pattern);
                        if first {
                            out.push_str(&format!("if (__m === {}) return {}; ", pattern_js, self.transpile_expr(&arm.body)));
                            first = false;
                        } else {
                            out.push_str(&format!("else if (__m === {}) return {}; ", pattern_js, self.transpile_expr(&arm.body)));
                        }
                    }
                }
                out.push_str("})()");
                out
            }

            // Range → Array from start..end
            Expr::Range { start, end } => {
                format!("Array.from({{length: {} - {}}}, (_, i) => i + {})",
                    self.transpile_expr(end), self.transpile_expr(start), self.transpile_expr(start))
            }

            // Logical NOT
            Expr::Not(expr) => {
                format!("(!{})", self.transpile_expr(expr))
            }
        }
    }

    /// Transpile method as JS class-method syntax (no 'function' keyword)
    fn transpile_class_method(&self, stmt: &Stmt, depth: usize) -> String {
        let pad = self.indent(depth);
        if let Stmt::FunctionDef { is_async, name, params, body, .. } = stmt {
            let async_kw = if *is_async { "async " } else { "" };
            let param_list: Vec<String> = params.iter().map(|(n, _)| n.clone()).collect();
            let mut body_str = String::new();
            for b_stmt in body {
                body_str.push_str(&self.transpile_stmt(b_stmt, depth + 1));
                body_str.push('\n');
            }
            format!("{}{}{}({}) {{\n{}{}}}", pad, async_kw, name, param_list.join(", "), body_str, pad)
        } else {
            self.transpile_stmt(stmt, depth)
        }
    }
}

