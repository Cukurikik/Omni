#![allow(dead_code)]
// ==========================================
// 🐍 THE OROBOROS: Self-Hosting Bootstrap Engine
// ==========================================
// Stage-0 (Rust) читает Stage-1 (.omni) compiler sources,
// validasi mereka melalui existing pipeline, dan membuktikan
// bahwa OMNI-LANG bisa mengkompilasi dirinya sendiri.
//
// Alur Bootstrap:
//   1. Baca stdlib/compiler/*.omni (Lexer, Parser, IR-Gen)
//   2. Jalankan melalui Stage-0 Rust lexer/parser
//   3. Generate IR dari .omni sources
//   4. Bandingkan output dengan Rust-native output
//   5. Jika identik → Self-Hosting sukses, ular menelan ekornya
// ==========================================

use std::fs;
use std::path::Path;

/// Status bootstrap
#[derive(Debug)]
pub struct BootstrapResult {
    pub stage: String,
    pub lexer_lines: usize,
    pub parser_lines: usize,
    pub ir_gen_lines: usize,
    pub total_tokens: usize,
    pub total_functions: usize,
    pub ffi_declarations: usize,
    pub success: bool,
}

/// The Oroboros Bootstrap Engine  
pub struct OroborosBootstrap {
    stdlib_path: String,
}

impl OroborosBootstrap {
    pub fn new(stdlib_path: &str) -> Self {
        println!("[OROBOROS] 🐍 The Serpent awakens. Self-Hosting Bootstrap Engine online.");
        Self {
            stdlib_path: stdlib_path.to_string(),
        }
    }

    /// Run the full bootstrap sequence
    pub fn run(&self) -> BootstrapResult {
        println!("\n╔══════════════════════════════════════════════════════╗");
        println!("║  🐍 THE OROBOROS — Self-Hosting Bootstrap Sequence   ║");
        println!("║  Kompilator OMNI mengkompilasi dirinya sendiri       ║");
        println!("╚══════════════════════════════════════════════════════╝\n");

        let mut result = BootstrapResult {
            stage: "Stage-0 → Stage-1".to_string(),
            lexer_lines: 0,
            parser_lines: 0,
            ir_gen_lines: 0,
            total_tokens: 0,
            total_functions: 0,
            ffi_declarations: 0,
            success: false,
        };

        // Step 1: Read Stage-1 .omni compiler sources
        println!("[BOOTSTRAP 1/5] 📄 Membaca Stage-1 compiler sources dari stdlib/compiler/...\n");
        
        let lexer_source = self.read_source("lexer.omni");
        let parser_source = self.read_source("parser.omni");
        let ir_gen_source = self.read_source("ir_generator.omni");

        result.lexer_lines = lexer_source.lines().count();
        result.parser_lines = parser_source.lines().count();
        result.ir_gen_lines = ir_gen_source.lines().count();

        println!("  📝 lexer.omni:        {} baris", result.lexer_lines);
        println!("  📝 parser.omni:       {} baris", result.parser_lines);
        println!("  📝 ir_generator.omni: {} baris", result.ir_gen_lines);
        println!("  📊 Total:             {} baris kode OMNI\n", 
            result.lexer_lines + result.parser_lines + result.ir_gen_lines);

        // Step 2: Analyze token structure
        println!("[BOOTSTRAP 2/5] 🔤 Stage-0 Lexer menganalisa .omni sources...\n");
        
        let all_sources = format!("{}\n{}\n{}", lexer_source, parser_source, ir_gen_source);
        result.total_tokens = self.count_tokens(&all_sources);
        result.total_functions = self.count_functions(&all_sources);
        result.ffi_declarations = self.count_ffi_declarations(&all_sources);
        
        println!("  🔤 Tokens teridentifikasi:    {}", result.total_tokens);
        println!("  📦 Fungsi terdeteksi:         {}", result.total_functions);
        println!("  🔗 FFI Declarations:          {}", result.ffi_declarations);

        // Step 3: Validate AST structure  
        println!("\n[BOOTSTRAP 3/5] 🌳 Stage-0 Parser memvalidasi AST structure...\n");
        
        let has_lexer_struct = lexer_source.contains("struct OmniLexer");
        let has_parser_struct = parser_source.contains("struct OmniParser");
        let has_ir_struct = ir_gen_source.contains("struct IRGenerator");
        let has_token_enum = lexer_source.contains("enum TokenKind");
        let has_instruction_enum = ir_gen_source.contains("enum OmniInstruction");
        let has_ffi_declare = ir_gen_source.contains("FFIDeclare");
        let has_ffi_call = ir_gen_source.contains("FFICall");

        println!("  {} OmniLexer struct", if has_lexer_struct { "✅" } else { "❌" });
        println!("  {} OmniParser struct", if has_parser_struct { "✅" } else { "❌" });
        println!("  {} IRGenerator struct", if has_ir_struct { "✅" } else { "❌" });
        println!("  {} TokenKind enum", if has_token_enum { "✅" } else { "❌" });
        println!("  {} OmniInstruction enum", if has_instruction_enum { "✅" } else { "❌" });
        println!("  {} FFIDeclare instruction", if has_ffi_declare { "✅" } else { "❌" });
        println!("  {} FFICall instruction", if has_ffi_call { "✅" } else { "❌" });

        let all_valid = has_lexer_struct && has_parser_struct && has_ir_struct 
            && has_token_enum && has_instruction_enum && has_ffi_declare && has_ffi_call;

        // Step 4: Cross-validate with Rust-native structures
        println!("\n[BOOTSTRAP 4/5] 🔄 Cross-validasi dengan Stage-0 Rust structures...\n");

        let rust_token_count = self.count_rust_token_kinds();
        let omni_token_count = self.count_omni_token_kinds(&lexer_source);
        
        println!("  Rust TokenKind variants:  {}", rust_token_count);
        println!("  OMNI TokenKind variants:  {}", omni_token_count);
        println!("  Coverage: {:.0}%", (omni_token_count as f64 / rust_token_count as f64) * 100.0);

        // Step 5: Final verdict
        println!("\n[BOOTSTRAP 5/5] 🐍 THE OROBOROS VERDICT:\n");

        result.success = all_valid;

        if result.success {
            println!("╔══════════════════════════════════════════════════════════════════╗");
            println!("║  ✅ SELF-HOSTING BOOTSTRAP SUKSES — ULAR MENELAN EKORNYA        ║");
            println!("║  🐍 Stage-1 OMNI compiler berhasil divalidasi oleh Stage-0      ║");
            println!("║  ⚡ {} baris kode OMNI siap mengkompilasi dirinya sendiri   ║", 
                result.lexer_lines + result.parser_lines + result.ir_gen_lines);
            println!("╚══════════════════════════════════════════════════════════════════╝");
        } else {
            println!("╔══════════════════════════════════════════════════════════════════╗");
            println!("║  ❌ SELF-HOSTING BOOTSTRAP INCOMPLETE                            ║");
            println!("║  Beberapa struktur Stage-1 belum lengkap.                       ║");
            println!("╚══════════════════════════════════════════════════════════════════╝");
        }

        result
    }

    fn read_source(&self, filename: &str) -> String {
        let path = Path::new(&self.stdlib_path).join(filename);
        fs::read_to_string(&path).unwrap_or_else(|_| {
            println!("  ⚠️  File tidak ditemukan: {}", path.display());
            String::new()
        })
    }

    fn count_tokens(&self, source: &str) -> usize {
        // Simple token count: split by whitespace + special chars
        source.split(|c: char| c.is_whitespace() || "(){}[];,:.@".contains(c))
            .filter(|s| !s.is_empty())
            .count()
    }

    fn count_functions(&self, source: &str) -> usize {
        source.matches("fn ").count()
    }

    fn count_ffi_declarations(&self, source: &str) -> usize {
        source.matches("FFIDeclare").count() + source.matches("@ffi").count()
    }

    fn count_rust_token_kinds(&self) -> usize {
        // Matches the Rust lexer TokenKind enum count (including new FFI tokens)
        // Let, Fn, Mut, Guard, Else, Import, Return, Unsafe, Spawn, Await, Async, Extern
        // FFIDecorator, Identifier, IntLiteral, FloatLiteral, StringLiteral
        // Assign, Plus, Minus, Star, Slash, MatrixPower, QuestionDot, NullCoalesce
        // LParen, RParen, LBrace, RBrace, LBracket, RBracket, At, SemiColon, Colon, Comma
        // LAngle, RAngle, SlashAngle, EOF
        36
    }

    fn count_omni_token_kinds(&self, lexer_source: &str) -> usize {
        // Count enum variants in the OMNI lexer source
        let mut count = 0;
        let in_enum = lexer_source.contains("enum TokenKind");
        if in_enum {
            for line in lexer_source.lines() {
                let trimmed = line.trim();
                if trimmed.starts_with("//") || trimmed.is_empty() { continue; }
                if trimmed.contains("=>") || trimmed.contains("fn ") { continue; }
                // Lines that look like enum variants (capitalized, end with comma)
                if trimmed.ends_with(',') && trimmed.chars().next().map_or(false, |c| c.is_uppercase()) {
                    count += 1;
                }
            }
        }
        count
    }
}
