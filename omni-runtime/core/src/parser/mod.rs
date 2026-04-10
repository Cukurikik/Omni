// ==========================================
// 🧬 OMNI-LANG PARSER (PEG/PEST Engine)
// ==========================================
// Modul ini menghubungkan gramatika PEST (.pest)
// dengan AST Builder, menghasilkan AST Program
// yang siap di-lower ke LLVM IR oleh Compiler Backend.
// ==========================================

pub mod ast;
pub mod lexer;
pub mod builder;

pub use ast::*;

use pest_derive::Parser;

/// OmniParser — Pest-derived PEG parser untuk bahasa OMNI.
/// Gramatika didefinisikan di `omni.pest`.
#[derive(Parser)]
#[grammar = "parser/omni.pest"]
pub struct OmniParser;

/// Convenience: Parse source code `.omni` menjadi AST `Program`.
pub fn parse_omni_source(source: &str) -> Result<Program, String> {
    use pest::Parser;
    let pairs = OmniParser::parse(Rule::OmniProgram, source)
        .map_err(|e| format!("Parse error: {}", e))?;

    // Ambil inner pairs dari OmniProgram
    let program_pair = pairs.into_iter().next()
        .ok_or_else(|| "Empty parse result".to_string())?;

    builder::build_ast(program_pair.into_inner())
}
