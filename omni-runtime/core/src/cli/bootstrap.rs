// ==========================================
// 🐍 OMNI BOOTSTRAP: CLI Command
// ==========================================
// omni bootstrap — menjalankan self-hosting bootstrap
// Membaca Stage-1 .omni compiler sources dan memvalidasinya
// menggunakan Stage-0 Rust compiler.
// ==========================================

use crate::selfhost::OroborosBootstrap;

pub fn run() {
    println!("$ omni bootstrap\n");
    
    // Determine stdlib path - try relative paths
    let possible_paths = vec![
        "stdlib/compiler",
        "../stdlib/compiler",
        "../../stdlib/compiler",
    ];

    let mut found_path = None;
    for path in &possible_paths {
        if std::path::Path::new(path).exists() {
            found_path = Some(path.to_string());
            break;
        }
    }

    let stdlib_path = match found_path {
        Some(p) => p,
        None => {
            println!("⚠️  stdlib/compiler/ tidak ditemukan.");
            println!("   Menggunakan path default. Buat direktori stdlib/compiler/ terlebih dahulu.");
            println!("   Jalankan dari root OMNI project directory.\n");
            "stdlib/compiler".to_string()
        }
    };

    let bootstrap = OroborosBootstrap::new(&stdlib_path);
    let result = bootstrap.run();

    // Print summary
    println!("\n📊 Bootstrap Summary:");
    println!("   Stage:           {}", result.stage);
    println!("   Lexer:           {} baris", result.lexer_lines);
    println!("   Parser:          {} baris", result.parser_lines);
    println!("   IR Generator:    {} baris", result.ir_gen_lines);
    println!("   Total Functions: {}", result.total_functions);
    println!("   FFI Bindings:    {}", result.ffi_declarations);
    println!("   Status:          {}", if result.success { "✅ SUKSES" } else { "❌ INCOMPLETE" });
}
