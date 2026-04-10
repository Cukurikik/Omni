// ═══════════════════════════════════════════════════════════
// 🐚 OMNI REPL — Interactive Shell
// ═══════════════════════════════════════════════════════════
// omni-daemon --shell
//
// Evaluasi kode OMNI secara interaktif dengan state persisten.
// Setiap input di-parse, di-transpile, dan dieksekusi di V8 ASLI.
// ═══════════════════════════════════════════════════════════

use crate::compiler::lexer::Lexer;
use crate::compiler::parser::Parser;
use crate::singularity::v8_micro_isolate::V8MicroIsolate;
use crate::singularity::transpiler::OmniTranspiler;
use crate::stdlib::runtime;
use std::io::{self, Write, BufRead};

/// OMNI REPL Session — menyimpan state antar evaluasi
pub struct OmniRepl {
    /// Akumulasi semua statement OMNI yang sudah diinput
    history_source: Vec<String>,
    /// Akumulasi JS yang sudah di-transpile (untuk re-execution)
    history_js: Vec<String>,
    /// V8 Engine
    v8: V8MicroIsolate,
    /// Transpiler
    transpiler: OmniTranspiler,
    /// Jumlah baris output terakhir (untuk diff)
    last_output_count: usize,
    /// Counter evaluasi
    eval_count: usize,
}

impl OmniRepl {
    pub fn new() -> Self {
        Self {
            history_source: Vec::new(),
            history_js: Vec::new(),
            v8: V8MicroIsolate::new(),
            transpiler: OmniTranspiler::new(false),
            last_output_count: 0,
            eval_count: 0,
        }
    }

    /// Jalankan REPL loop
    pub fn run(&mut self) {
        // Banner
        self.print_banner();

        // Inisialisasi V8
        if let Err(e) = self.v8.initialize() {
            eprintln!("❌ Gagal menginisialisasi V8: {}", e);
            return;
        }
        println!();

        let stdin = io::stdin();
        let mut multiline_buffer = String::new();
        let mut brace_depth: i32 = 0;

        loop {
            // Prompt
            if brace_depth > 0 {
                print!("  ... │ ");
            } else {
                print!("omni[{}]› ", self.eval_count);
            }
            io::stdout().flush().unwrap();

            // Baca input
            let mut line = String::new();
            match stdin.lock().read_line(&mut line) {
                Ok(0) => {
                    // EOF (Ctrl+D)
                    println!("\n👋 Sampai jumpa!");
                    break;
                }
                Ok(_) => {}
                Err(e) => {
                    eprintln!("❌ Error baca input: {}", e);
                    continue;
                }
            }

            let trimmed = line.trim();

            // ─── Perintah Khusus ────────────────────────
            if brace_depth == 0 {
                match trimmed {
                    "" => continue,
                    ":quit" | ":q" | ":exit" => {
                        println!("👋 Sampai jumpa, Kapten!");
                        break;
                    }
                    ":help" | ":h" => {
                        self.print_help();
                        continue;
                    }
                    ":clear" | ":c" => {
                        self.history_source.clear();
                        self.history_js.clear();
                        self.last_output_count = 0;
                        self.eval_count = 0;
                        println!("🗑️  State di-reset. Memori bersih.");
                        continue;
                    }
                    ":history" => {
                        if self.history_source.is_empty() {
                            println!("📜 (kosong)");
                        } else {
                            println!("📜 History:");
                            for (i, s) in self.history_source.iter().enumerate() {
                                println!("  [{}] {}", i, s.replace('\n', "\n      "));
                            }
                        }
                        continue;
                    }
                    ":ast" => {
                        self.show_last_ast();
                        continue;
                    }
                    ":js" => {
                        self.show_last_js();
                        continue;
                    }
                    ":std" => {
                        println!("📦 omni-std v2.0.0 — Modul Tersedia:");
                        for module in runtime::list_modules() {
                            println!("  • {}", module);
                        }
                        continue;
                    }
                    _ => {}
                }
            }

            // ─── Multi-line Detection ───────────────────
            // Hitung brace depth
            for ch in trimmed.chars() {
                if ch == '{' { brace_depth += 1; }
                if ch == '}' { brace_depth -= 1; }
            }

            multiline_buffer.push_str(&line);

            // Jika masih dalam blok, lanjut baca
            if brace_depth > 0 {
                continue;
            }

            // Reset jika negatif (lebih banyak } dari {)
            if brace_depth < 0 {
                brace_depth = 0;
            }

            // ─── Evaluasi ───────────────────────────────
            let input = multiline_buffer.trim().to_string();
            multiline_buffer.clear();

            if !input.is_empty() {
                self.evaluate(&input);
                self.eval_count += 1;
            }
        }
    }

    /// Evaluasi satu blok kode OMNI
    fn evaluate(&mut self, source: &str) {
        // 1. Lexer + Parser
        let lexer = Lexer::new(source);
        let mut parser = Parser::new(lexer);
        let ast = parser.parse_program();

        if ast.statements.is_empty() {
            println!("⚠️  Tidak ada statement yang bisa di-parse.");
            return;
        }

        // 2. Transpile AST → JavaScript
        let js_code = self.transpiler.transpile(&ast);

        // 3. Simpan di history
        self.history_source.push(source.to_string());
        self.history_js.push(js_code.clone());

        // 4. Gabungkan semua JS history dan eksekusi
        let full_js = self.history_js.join("\n");

        // 5. Eksekusi di V8
        match self.v8.execute(&full_js) {
            Ok(output) => {
                if output.is_empty() {
                    return;
                }
                let all_lines: Vec<&str> = output.lines().collect();
                let new_lines = &all_lines[self.last_output_count..];

                if !new_lines.is_empty() {
                    for line in new_lines {
                        println!("  ⇒ {}", line);
                    }
                }
                self.last_output_count = all_lines.len();
            }
            Err(e) => {
                // Error — rollback history
                self.history_source.pop();
                self.history_js.pop();

                let err_str = e.to_string();
                // Tampilkan error yang bersih
                if let Some(msg) = err_str.strip_prefix("❌ V8 Runtime Error: ") {
                    println!("  ❌ {}", msg.lines().next().unwrap_or(&err_str));
                } else {
                    println!("  ❌ {}", err_str.lines().next().unwrap_or(&err_str));
                }
            }
        }
    }

    /// Tampilkan AST terakhir
    fn show_last_ast(&self) {
        if let Some(source) = self.history_source.last() {
            let lexer = Lexer::new(source);
            let mut parser = Parser::new(lexer);
            let ast = parser.parse_program();
            println!("🌳 AST terakhir:");
            for (i, stmt) in ast.statements.iter().enumerate() {
                println!("  [{}] {:?}", i, stmt);
            }
        } else {
            println!("📜 (belum ada kode)");
        }
    }

    /// Tampilkan JS terakhir
    fn show_last_js(&self) {
        if let Some(js) = self.history_js.last() {
            println!("📜 JavaScript terakhir:");
            println!("────────────────────────────────");
            println!("{}", js);
            println!("────────────────────────────────");
        } else {
            println!("📜 (belum ada kode)");
        }
    }

    /// Banner pembuka
    fn print_banner(&self) {
        println!();
        println!("╔══════════════════════════════════════════════════════╗");
        println!("║  🐚 OMNI SHELL — Interactive REPL v2.0              ║");
        println!("║  Powered by rusty_v8 + omni-std                     ║");
        println!("╠══════════════════════════════════════════════════════╣");
        println!("║  Ketik kode OMNI lalu Enter untuk evaluasi.         ║");
        println!("║  Ketik :help untuk bantuan. :quit untuk keluar.     ║");
        println!("╚══════════════════════════════════════════════════════╝");
    }

    /// Bantuan
    fn print_help(&self) {
        println!();
        println!("═══ OMNI SHELL — Perintah ═══");
        println!();
        println!("  :help, :h      Tampilkan bantuan ini");
        println!("  :quit, :q      Keluar dari shell");
        println!("  :clear, :c     Reset semua state");
        println!("  :history       Tampilkan riwayat input");
        println!("  :ast           Tampilkan AST dari input terakhir");
        println!("  :js            Tampilkan JavaScript dari input terakhir");
        println!("  :std           Tampilkan modul omni-std yang tersedia");
        println!();
        println!("═══ Contoh Kode ═══");
        println!();
        println!("  let x: Int = 42");
        println!("  print(x)");
        println!("  fn add(a: Int, b: Int) -> Int {{ return a + b }}");
        println!("  print(add(10, 20))");
        println!("  let v: Float = 3.0 .* 4.0");
        println!("  print(OmniMath.mean([1,2,3,4,5]))");
        println!();
    }
}
