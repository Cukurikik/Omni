use std::fs;
use std::process::Command;
use omnicore::singularity::transpiler::OmniTranspiler;
use omnicore::compiler::optimizer::OmniOptimizer;
use super::project::OmniProject;
use std::env;

pub struct OmniBuilder;

impl OmniBuilder {
    pub fn build(is_release: bool, _target_dir: Option<String>) {
        println!("⚙️ [BUILD] Memulai OMNI Compilation Pipeline...");
        
        // 1. Tentukan file entry
        let entrypoint = match OmniProject::find_entrypoint() {
            Some(path) => path,
            None => {
                eprintln!("❌ Error: Tidak dapat menemukan file entrypoint untuk di-build.");
                return;
            }
        };

        println!("📄 [FILE] Sumber kode utama: {}", entrypoint.display());

        // 3. Parsing & Nexus Bundling
        let mut nexus = omnicore::compiler::nexus::OmniNexus::new();
        let mut ast = match nexus.bundle(&entrypoint) {
            Ok(prog) => prog,
            Err(e) => {
                eprintln!("❌ [NEXUS] Gagal bundling modul: {}", e);
                return;
            }
        };

        // 3.5 [OPTIMIZER] Tree Shaking
        if is_release {
            let optimizer = OmniOptimizer::new();
            optimizer.optimize_ast(&mut ast);
        }

        // 4. Transpile ke JS Payload
        let transpiler = OmniTranspiler::new(is_release);
        let js_payload = transpiler.transpile(&ast);

        if is_release {
            println!("🔄 [MINIFY] AST berhasil diminifikasi (Release Mode aktif).");
        }

        // 5. Build Native Executable
        println!("📦 [PACKAGE] Merakit Standalone Native Binary (.exe)...");

        if let Err(e) = Self::compile_standalone_binary(&js_payload, is_release) {
            eprintln!("❌ [FATAL] Gagal membangun binary: {}", e);
        } else {
            println!("✅ [SUCCESS] OMNI Project berhasil dikompilasi ke Native Executable!");
        }
    }

    /// Strategi: Buat folder `.omni_cache/` di dalam project,
    /// generate `main.rs` yang meng-embed JS Payload dan menjalankan `v8_micro_isolate`.
    /// Kompilasi menggunakan `cargo build`, lalu pindahkan hasilnya.
    fn compile_standalone_binary(js_payload: &str, is_release: bool) -> Result<(), String> {
        let current_dir = env::current_dir().map_err(|e| e.to_string())?;
        let cache_dir = current_dir.join(".omni_cache");
        let target_dir = current_dir.join("target");

        // Buat cache direktori
        if !cache_dir.exists() {
            fs::create_dir(&cache_dir).map_err(|e| e.to_string())?;
        }

        // Tulis AST JS Payload (Minified/Dev)
        let payload_path = cache_dir.join("payload.js");
        fs::write(&payload_path, js_payload).map_err(|e| e.to_string())?;

        // Generate Cargo.toml sementara untuk runner
        let omni_core_path = env::var("CARGO_MANIFEST_DIR")
            .unwrap_or_else(|_| "c:/Users/IKYY/Downloads/Omni/omni-runtime/core".to_string())
            .replace("\\", "/");

        let cargo_toml = format!(r#"[package]
name = "omni_runner"
version = "0.1.0"
edition = "2021"

[dependencies]
omnicore = {{ package = "omni-core", path = "{}" }}
"#, omni_core_path);

        fs::write(cache_dir.join("Cargo.toml"), cargo_toml).map_err(|e| e.to_string())?;

        // Generate src/main.rs runner
        let runner_src_dir = cache_dir.join("src");
        if !runner_src_dir.exists() {
            fs::create_dir(&runner_src_dir).map_err(|e| e.to_string())?;
        }

        let main_rs = r#"
use omnicore::singularity::v8_micro_isolate::V8MicroIsolate;

fn main() {
    let payload = include_str!("../payload.js");
    let mut micro_v8 = V8MicroIsolate::new();
    
    // Inisialisasi V8
    if let Err(e) = micro_v8.initialize() {
        eprintln!("❌ Native Engine Error: {}", e);
        return;
    }
    
    // Eksekusi Payload Tertanam
    match micro_v8.execute(payload) {
        Ok(output) => {
            if !output.is_empty() && output != "\"\"" {
                println!("{}", output.trim_matches('"').replace("\\n", "\n"));
            }
        }
        Err(e) => {
            eprintln!("❌ Omni Runtime Error: {}", e);
            std::process::exit(1);
        }
    }
}
"#;
        fs::write(runner_src_dir.join("main.rs"), main_rs).map_err(|e| e.to_string())?;

        // Jalankan Cargo Build di .omni_cache
        let mut cmd = Command::new("cargo");
        cmd.arg("build");
        if is_release {
            cmd.arg("--release");
        }
        cmd.current_dir(&cache_dir);

        let status = cmd.status().map_err(|e| format!("Gagal memanggil cargo: {}", e))?;
        if !status.success() {
            return Err("Kompilasi C++ / Rust backend gagal.".into());
        }

        // Pindahkan exe dari target/debug|release ke luar
        if !target_dir.exists() {
            fs::create_dir(&target_dir).map_err(|e| e.to_string())?;
        }

        let mode_dir = if is_release { "release" } else { "debug" };
        let exe_path = cache_dir.join("target").join(mode_dir).join("omni_runner.exe");

        let dest_exe = target_dir.join(format!("output_{}.exe", mode_dir));

        if exe_path.exists() {
            fs::copy(&exe_path, &dest_exe).map_err(|e| format!("Gagal mencopy exe: {}", e))?;
            println!("\n📦 Executable tersedia di: {}", dest_exe.display());
        } else {
            return Err(format!("Binary tidak ditemukan di {}", exe_path.display()));
        }

        Ok(())
    }
}
