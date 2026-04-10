use super::Rule;
use super::ast::*;
use pest::iterators::{Pair, Pairs};

pub fn build_ast(pairs: Pairs<Rule>) -> Result<Program, String> {
    let mut body = Vec::new();

    for pair in pairs {
        match pair.as_rule() {
            Rule::Statement => {
                body.push(build_statement(pair)?);
            }
            Rule::EOI => break,
            _ => {
                // Ignore or handle other top level items
            }
        }
    }

    Ok(Program { body })
}

fn build_statement(pair: Pair<Rule>) -> Result<Statement, String> {
    let inner = pair.into_inner().next().unwrap();
    match inner.as_rule() {
        Rule::Declaration => {
            let decl_inner = inner.into_inner().next().unwrap();
            match decl_inner.as_rule() {
                Rule::LetDecl => {
                    let mut inner_pairs = decl_inner.into_inner();
                    let name = inner_pairs.next().unwrap().as_str().to_string(); // Identifier
                    
                    // Skip optional type for now
                    let mut next_pair = inner_pairs.next().unwrap();
                    if next_pair.as_rule() == Rule::Type {
                        next_pair = inner_pairs.next().unwrap();
                    }
                    
                    let init_expr = build_expression(next_pair)?;
                    return Ok(Statement::LetBinding {
                        name,
                        value: init_expr,
                    });
                }
                Rule::FnDecl => {
                    let mut inner_pairs = decl_inner.into_inner();
                    let name = inner_pairs.next().unwrap().as_str().to_string();
                    // Skip params and return type for now, jump to block
                    let mut fn_body = Vec::new();
                    for p in inner_pairs {
                        if p.as_rule() == Rule::Block {
                            for block_stmt in p.into_inner() {
                                if block_stmt.as_rule() == Rule::Statement {
                                    fn_body.push(build_statement(block_stmt)?);
                                }
                            }
                        }
                    }
                    return Ok(Statement::FunctionDeclaration(FnDecl {
                        name,
                        params: Vec::new(),
                        return_type: None,
                        body: fn_body,
                    }));
                }
                _ => return Err("Unsupported declaration".into()),
            }
        }
        Rule::PolyglotBlock => {
            // PolyglotBlock as a top-level statement → wrap in ExprStmt
            let expr = build_expression(inner)?;
            return Ok(Statement::ExprStmt(expr));
        }
        Rule::Assignment => {
            // identifier = expression;
            let mut inner_pairs = inner.into_inner();
            let name = inner_pairs.next().unwrap().as_str().to_string();
            let value = build_expression(inner_pairs.next().unwrap())?;
            return Ok(Statement::LetBinding { name, value });
        }
        Rule::ReturnStatement => {
            let expr = build_expression(inner.into_inner().next().unwrap())?;
            return Ok(Statement::Return(expr));
        }
        Rule::ExpressionStmt => {
            let expr = build_expression(inner.into_inner().next().unwrap())?;
            return Ok(Statement::ExprStmt(expr));
        }
        Rule::UnsafeZone => {
            let mut inner_pairs = inner.into_inner();
            let name_raw = inner_pairs.next().unwrap().as_str(); // StringLiteral
            let name = name_raw.trim_matches('"').to_string();
            
            let block = inner_pairs.next().unwrap(); // Block
            let mut body = Vec::new();
            for block_stmt in block.into_inner() {
                if block_stmt.as_rule() == Rule::Statement {
                    body.push(build_statement(block_stmt)?);
                }
            }
            return Ok(Statement::UnsafeZone { name, body });
        }
        _ => Err(format!("Unsupported statement rule: {:?}", inner.as_rule())),
    }
}

fn build_expression(pair: Pair<Rule>) -> Result<Expr, String> {
    match pair.as_rule() {
        Rule::Expression => {
            let inner = pair.into_inner().next().unwrap();
            build_expression(inner)
        }
        Rule::PolyglotBlock => {
            let mut inner_pairs = pair.into_inner();
            let lang = inner_pairs.next().unwrap().as_str().to_string();
            let native_source = inner_pairs.next().unwrap(); // NativeSourceCode

            let mut source_code = String::new();
            let mut injected_pointers = Vec::new();
            let mut inject_idx = 0;

            for native_part in native_source.into_inner() {
                match native_part.as_rule() {
                    Rule::NativeText => {
                        source_code.push_str(native_part.as_str());
                    }
                    Rule::MemoryInjection => {
                        // format: $identifier
                        let mut inject_inner = native_part.into_inner();
                        let identifier = inject_inner.next().unwrap().as_str().to_string();
                        
                        let internal_name = format!("__OMNI_INJECT_{}__", inject_idx);
                        inject_idx += 1;
                        
                        source_code.push_str(&internal_name);
                        injected_pointers.push(InjectedPointer {
                            internal_name,
                            references_to: identifier,
                        });
                    }
                    _ => {}
                }
            }

            Ok(Expr::PolyglotNode(PolyglotNode {
                language: lang,
                source_code,
                injected_pointers,
            }))
        }
        Rule::Identifier => Ok(Expr::Identifier(pair.as_str().to_string())),
        Rule::StringLiteral => Ok(Expr::StringLiteral(pair.as_str().to_string())),
        Rule::NumberLiteral => Ok(Expr::NumberLiteral(pair.as_str().parse().unwrap())),
        _ => Err(format!("Unsupported expression rule: {:?}", pair.as_rule())),
    }
}
