use std::fs;
use std::path::PathBuf;
use std::env;

pub struct OmniProject;

impl OmniProject {
    pub fn new() -> Self {
        OmniProject
    }

    pub fn init(&self, project_name: &str) {
        let base_path = PathBuf::from(project_name);
        
        if base_path.exists() {
            eprintln!("❌ Error: Direktori '{}' sudah ada.", project_name);
            return;
        }

        // Buat folder proyek
        if let Err(e) = fs::create_dir(&base_path) {
            eprintln!("❌ Error: Gagal membuat direktori '{}': {}", project_name, e);
            return;
        }

        // Buat folder src/
        let src_path = base_path.join("src");
        if let Err(e) = fs::create_dir(&src_path) {
            eprintln!("❌ Error: Gagal membuat direktori src/: {}", e);
            return;
        }

        // Buat folder tests/
        let tests_path = base_path.join("tests");
        if let Err(e) = fs::create_dir(&tests_path) {
            eprintln!("❌ Error: Gagal membuat direktori tests/: {}", e);
            return;
        }

        // Buat file Omnifile.toml
        let omnifile_path = base_path.join("Omnifile.toml");
        let toml_content = format!(r#"[package]
name = "{}"
version = "0.1.0"
authors = ["Omni Developer <dev@omni.nexus>"]
description = "A new OMNI 15-paradigm standard project"
edition = "omni-2025"

[dependencies]
omni-std = "^2.0"

[permissions]
allow_net = []
allow_fs = []
allow_env = []
allow_thread = true

[build]
target = ["wasm32", "x86_64-linux", "aarch64-apple"]
optimize = "release"
"#, project_name);
        
        if let Err(e) = fs::write(&omnifile_path, toml_content) {
            eprintln!("❌ Error: Gagal menulis Omnifile.toml: {}", e);
            return;
        }

        // Buat file src/main.omni
        let main_path = src_path.join("main.omni");
        let main_content = format!(r#"/// Entry point of the OMNI application: {}

@system::core
fn main() -> Void {{
    immutable val app_config_name = "OMNI Nexus";
    
    // Default HTTP routine via Goroutine pattern
    @network::go
    spawn server_routine();

    print("Status: Application Initialized.");
}}

fn server_routine() -> Void {{
    print("Server worker thread started...");
}}
"#, project_name);

        if let Err(e) = fs::write(&main_path, main_content) {
            eprintln!("❌ Error: Gagal menulis src/main.omni: {}", e);
            return;
        }

        // README.md
        let readme_path = base_path.join("README.md");
        let readme_content = format!(r#"# {}
This is an OMNI project.

## Development
- Run project: `omni run`
- Build project: `omni build`
- Check types and AST: `omni check`
"#, project_name);
        
        if let Err(e) = fs::write(&readme_path, readme_content) {
            eprintln!("❌ Error: Gagal menulis README.md: {}", e);
            return;
        }

        println!("✅ Berhasil membuat proyek OMNI '{}'!", project_name);
        println!("   Gunakan perintah berikut untuk mulai:");
        println!("   $ cd {}", project_name);
        println!("   $ omni run");
    }

    /// Mencari Omnifile.toml ke direktori root, lalu mencari entry point `src/main.omni`
    pub fn find_entrypoint() -> Option<PathBuf> {
        let current_dir = env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
        let mut check_dir = Some(current_dir.as_path());

        while let Some(dir) = check_dir {
            let omni_file = dir.join("Omnifile.toml");
            if omni_file.exists() {
                let main_file = dir.join("src").join("main.omni");
                if main_file.exists() {
                    return Some(main_file);
                }
                
                let lib_file = dir.join("src").join("lib.omni");
                if lib_file.exists() {
                    return Some(lib_file);
                }
                return None;
            }
            check_dir = dir.parent();
        }

        // Fallback: Jika tidak ada file project, gunakan path lokal
        let local_main = PathBuf::from("src/main.omni");
        if local_main.exists() {
            return Some(local_main);
        }
        
        None
    }
}
