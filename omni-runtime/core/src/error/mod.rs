// ==========================================
// 🚨 OMNI-LANG DIAGNOSTICS: THE ERROR REPORTER
// ==========================================
// Mesin pelaporan error ala Elm/Rust yang ramah manusia.
// Jika terjadi error (Sintaks, Type, atau Null-Safety),
// akan di-render sebagai pesan visual dengan petunjuk
// rekomendasi kode (Auto-fix suggestions).
// ==========================================

#[derive(Debug, Clone)]
pub enum OmniErrorKind {
    NullSafetyViolation,
    TypeMismatch { expected: String, found: String },
    UseAfterFree,
    SyntaxError,
}

#[derive(Debug, Clone)]
pub struct OmniDiagnostic {
    pub kind: OmniErrorKind,
    pub file_path: String,
    pub line: usize,
    pub column: usize,
    pub message: String,
    pub snippet: String,
    pub recommendation: Option<String>,
}

pub struct DiagnosticEngine;

impl DiagnosticEngine {
    pub fn report(diagnostic: OmniDiagnostic) {
        println!("\n❌ [OMNI-VAULT ERROR]: {}", diagnostic.message);
        println!("   --> {}:{}:{}", diagnostic.file_path, diagnostic.line, diagnostic.column);
        println!("    |");
        // Formatting snippet (di versi nyata akan membaca konten file asli)
        println!("{:4}|    {}", diagnostic.line, diagnostic.snippet);
        println!("    |    {}^ {}", " ".repeat(diagnostic.column - 1), "Peringatan kritis!");
        println!("    |");
        
        if let Some(solution) = diagnostic.recommendation {
            println!(" 💡 SOLUSI MUTLAK:");
            println!("    {}", solution);
        }
        println!();
    }

    pub fn demo_null_safety_error() {
        Self::report(OmniDiagnostic {
            kind: OmniErrorKind::NullSafetyViolation,
            file_path: "src/dashboard.omni".to_string(),
            line: 14,
            column: 21,
            message: "Pelanggaran Null-Safety!".to_string(),
            snippet: "let id_length = user_id.length();".to_string(),
            recommendation: Some("Gunakan 'guard let' (Gaya Swift) atau operator opsional '?.' (Gaya TS).\n    Coba ubah menjadi:\n    let id_length = user_id?.length() ?? 0;".to_string()),
        });
    }
}
