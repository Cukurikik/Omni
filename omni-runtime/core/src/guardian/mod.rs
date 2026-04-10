pub mod segregation;
pub mod result;
pub mod formatter;

use segregation::RoleBasedLinter;
use result::OmniResultProtocol;
use formatter::SemanticAutoIdiom;

pub struct OmniGuardian {
    linter: RoleBasedLinter,
    protocol: OmniResultProtocol,
    formatter: SemanticAutoIdiom,
}

impl OmniGuardian {
    pub fn new() -> Self {
        Self {
            linter: RoleBasedLinter::new(),
            protocol: OmniResultProtocol::new(),
            formatter: SemanticAutoIdiom::new(),
        }
    }

    /// Entry point for strict architectural enforcement
    pub fn enforce_strict_compliance(&self, file_path: &str, ast_memory_node: &str) -> Result<(), String> {
        // 1. Role-Based Segregation: Check if language extension matches allowed domain logic
        self.linter.validate_domain_bounds(file_path, ast_memory_node)?;

        // 2. The Unified Result Type: Check if the node adheres to Monadic Error Handling
        if !self.protocol.has_proper_error_handling(ast_memory_node) {
            return Err(format!("❌ [OMNI-GUARDIAN] FATAL: File {} mengabaikan error handling! Gunakan paradigma OmniResult dengan blok `match (result) {{ Ok(_), Err(_) }}`.", file_path));
        }

        Ok(())
    }

    /// Entry point for code auto-formatting (Auto Idiom)
    pub fn format_semantic_idioms(&self, file_path: &str, raw_code: &str) -> String {
        self.formatter.apply_zen_of_omni(file_path, raw_code)
    }
}
