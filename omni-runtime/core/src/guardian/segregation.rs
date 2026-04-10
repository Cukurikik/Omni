pub struct RoleBasedLinter;

impl RoleBasedLinter {
    pub fn new() -> Self {
        RoleBasedLinter
    }

    /// Evaluates if a given source file delegates responsibilities correctly
    pub fn validate_domain_bounds(&self, file_path: &str, ast_memory_node: &str) -> Result<(), String> {
        if file_path.ends_with(".ts") || file_path.ends_with(".html") || file_path.ends_with(".swift") {
            // ONLY UI logic allowed. No db/sql accesses.
            if ast_memory_node.contains("USE_SQL") || ast_memory_node.contains("DB_DRIVER") {
                return Err(format!("❌ [OMNI-GUARDIAN] ROLE VIOLATION in {}: File Frontend (UI) DILARANG keras menyentuh abstraksi Database. Pindahkan logika ke rust/c/cpp atau layer Backend.", file_path));
            }
        } else if file_path.ends_with(".rs") || file_path.ends_with(".c") || file_path.ends_with(".cpp") {
            // ONLY Memory, Hardware, Crypto, DB allowed. No UI logic.
            if ast_memory_node.contains("USE_REACT_RENDER") || ast_memory_node.contains("DOM_MANIPULATION") {
                return Err(format!("❌ [OMNI-GUARDIAN] ROLE VIOLATION in {}: File Tingkat Rendah (Low-Level) DILARANG merender UI Component. Kembalikan data dan biarkan file Frontend berekspresi.", file_path));
            }
        } else if file_path.ends_with(".py") || file_path.ends_with(".jl") {
            // ONLY Tensor, AI, Heavy Compute
            if ast_memory_node.contains("ROUTER_HTTP") || ast_memory_node.contains("SERVING_STATIC") {
                 return Err(format!("❌ [OMNI-GUARDIAN] ROLE VIOLATION in {}: File Julia/Python dikhususkan untuk komputasi AI/Tensor, BUKAN sebagai Web Server. Gunakan abstraksi Web server di TS/Rust.", file_path));
            }
        }
        
        // Ensure "The One Way" library calls
        if ast_memory_node.contains("fs.readFileSync") || ast_memory_node.contains("os.Open") || ast_memory_node.contains("open(") {
            return Err(format!("❌ [OMNI-GUARDIAN] STANDARD LIB VIOLATION in {}: Tinggalkan library kuno platform-dependent. Mutlak gunakan Standard Library Universal `std:fs` OMNI.", file_path));
        }

        Ok(())
    }
}
