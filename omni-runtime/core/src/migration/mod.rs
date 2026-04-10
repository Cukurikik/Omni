pub mod ast_mapper;
pub mod transpiler;

pub use ast_mapper::{LegacyLanguage, LegacyASTToken, OmniASTNode, map_to_omni};
pub use transpiler::{transpile_to_omni, transpile_to_legacy};

pub struct MigrationEngine;

impl MigrationEngine {
    pub fn new() -> Self {
        Self
    }

    /// Translates source code from a legacy language to OMNI
    pub fn assimilate(&self, source: &str, lang: LegacyLanguage) -> Result<String, String> {
        let engine = ast_mapper::DeterministicAstEngine::new();
        let tokens = engine.translate(source, lang)?;
        let omni_ast = ast_mapper::map_to_omni(tokens)?;
        Ok(transpiler::transpile_to_omni(&omni_ast))
    }
}
