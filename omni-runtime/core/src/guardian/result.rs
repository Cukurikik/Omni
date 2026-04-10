pub struct OmniResultProtocol;

impl OmniResultProtocol {
    pub fn new() -> Self {
        OmniResultProtocol
    }

    /// Verifies that all IO/Network calls explicitly match `Ok()` and `Err()`
    pub fn has_proper_error_handling(&self, ast_memory_node: &str) -> bool {
        // If the AST dictates an IO operation..
        if ast_memory_node.contains("IO_OPERATION") || ast_memory_node.contains("NETWORK_REQ") {
            // It MUST contain standard OmniResult matching keywords
            if !ast_memory_node.contains("Omni_Match_Ok") || !ast_memory_node.contains("Omni_Match_Err") {
                return false;
            }
        }
        true
    }
}
