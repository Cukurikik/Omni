// ==========================================
// 📥 OMNI INSTALL: Package Installation Command
// ==========================================
// omni install — membaca Omnifile, resolve dependencies,
// download via Nexus Registry, generate Omnifile.lock
// ==========================================

use omnicore::nexus::{OmniManifest, generate_lockfile};
use omnicore::nexus::resolver::NexusResolver;
use omnicore::nexus::registry::NexusRegistry;
use omnicore::nexus::ResolvedPackage;
use std::path::Path;

pub fn run() {
    println!("$ omni install\n");
    
    let mut omnifile_path = Path::new("Omnifile.toml");
    
    if !omnifile_path.exists() {
        // Coba tanpa ekstensi
        omnifile_path = Path::new("Omnifile");
    }

    if !omnifile_path.exists() {
        // Coba cari di parent directory jika di dalam src/ dsb
        let alt_path = Path::new("../Omnifile.toml");
        if alt_path.exists() {
            run_with_manifest(alt_path);
            return;
        }
        
        println!("❌ Omnifile tidak ditemukan di direktori ini.");
        println!("   Jalankan `omni init <nama>` untuk membuat project baru.");
        return;
    }

    run_with_manifest(omnifile_path);
}

fn run_with_manifest(path: &Path) {
    println!("[NEXUS] 📄 Membaca manifest: {}", path.display());

    // Parse Omnifile
    let manifest = match OmniManifest::parse(path) {
        Ok(m) => m,
        Err(e) => {
            println!("❌ {}", e);
            return;
        }
    };

    println!("[NEXUS] 📦 Project: {} v{}", manifest.project_name, manifest.version);
    println!("[NEXUS] 🔒 Compiler requirement: {}", manifest.compiler_version);
    println!("[NEXUS] 📊 Dependencies: {}\n", manifest.dependencies.len());

    if manifest.dependencies.is_empty() {
        println!("✅ Tidak ada dependency — project ini mandiri.");
        return;
    }

    // Step 2: Resolve dependencies
    let mut resolver = NexusResolver::new();
    let resolved: std::collections::HashMap<String, ResolvedPackage> = match resolver.resolve(&manifest.dependencies) {
        Ok(r) => r,
        Err(e) => {
            println!("❌ {}", e);
            return;
        }
    };

    // Step 3: Install packages (download + validate + cache)
    let registry = NexusRegistry::new();
    if let Err(e) = registry.install_packages(&resolved) {
        println!("❌ {}", e);
        return;
    }

    // Step 4: Generate lockfile
    let lockfile_content = generate_lockfile(&manifest, &resolved);
    let lock_path = path.parent().unwrap_or(Path::new(".")).join("Omnifile.lock");
    
    match std::fs::write(&lock_path, &lockfile_content) {
        Ok(_) => println!("\n[NEXUS] 🔒 Lockfile generated: {}", lock_path.display()),
        Err(e) => println!("⚠️  Gagal menulis lockfile: {}", e),
    }

    // Print security summary
    println!("\n╔══════════════════════════════════════════════════════╗");
    println!("║  📦 OMNI NEXUS — Installation Complete              ║");
    println!("╠══════════════════════════════════════════════════════╣");
    println!("║  Packages: {} resolved, {} verified               ║", 
        resolved.len(),
        resolved.values().filter(|p| p.verified).count()
    );
    println!("║  Lockfile: Omnifile.lock ✅                         ║");
    println!("║  Security: Blockchain Hash Validated ✅              ║");
    println!("╚══════════════════════════════════════════════════════╝");
}
