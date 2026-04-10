// ==========================================
// 🏢 NEXUS WORKSPACE: Monorepo Orchestrator
// ==========================================
// Menangani arsitektur monorepo OMNI. Melewati
// pengunduhan HTTP dan memetakan package 
// internal secara langsung di level RAM/OS.
// ==========================================

use std::fs;
use std::path::{Path, PathBuf};
use std::os::windows::fs::symlink_dir;

#[derive(Debug, Clone)]
pub struct LocalPackage {
    pub name: String,
    pub path: PathBuf,
}

pub struct WorkspaceManager {
    root_dir: PathBuf,
    pub members: Vec<LocalPackage>,
}

impl WorkspaceManager {
    pub fn new(root_dir: PathBuf) -> Self {
        Self {
            root_dir,
            members: Vec::new(),
        }
    }

    /// Memindai Omnifile.toml untuk pola workspace (contoh: ["apps/*", "packages/*"])
    pub fn scan_workspace(&mut self, patterns: &[&str]) {
        println!("🏢 [OMNI-WORKSPACE] Memindai Monorepo Root: {:?}", self.root_dir);
        
        for pattern in patterns {
            let base_folder = pattern.trim_end_matches("/*");
            let target_dir = self.root_dir.join(base_folder);
            
            if target_dir.exists() && target_dir.is_dir() {
                if let Ok(entries) = fs::read_dir(target_dir) {
                    for entry in entries.flatten() {
                        if entry.file_type().map_or(false, |ft| ft.is_dir()) {
                            let omnifile = entry.path().join("Omnifile.toml");
                            if omnifile.exists() {
                                // Ekstrak nama paket sederhana pakai nama folder sebagai identifier
                                let pkg_name = entry.file_name().to_string_lossy().to_string();
                                println!("  📦 Ditemukan Paket Internal: {}", pkg_name);
                                self.members.push(LocalPackage {
                                    name: pkg_name,
                                    path: entry.path(),
                                });
                            }
                        }
                    }
                }
            }
        }
    }

    /// Zero-Copy Local Binding
    /// Membuat symlink di folder tujuan ke memori lokal
    pub fn construct_local_binding(&self, local_pkg: &LocalPackage, target_omni_modules: &Path) -> Result<(), String> {
        if !target_omni_modules.exists() {
            fs::create_dir_all(target_omni_modules).unwrap_or(());
        }

        let link_dest = target_omni_modules.join(&local_pkg.name);
        
        // Bersihkan bekas link jika ada
        if link_dest.exists() || link_dest.read_link().is_ok() {
            let _ = fs::remove_dir_all(&link_dest);
            let _ = fs::remove_file(&link_dest);
        }

        println!("  🔗 Menambatkan (Zero-Copy): {} -> {:?}", local_pkg.name, local_pkg.path);
        
        // Membutuhkan Hak Akses Administrator atau Developer Mode di Windows
        if let Err(e) = symlink_dir(&local_pkg.path, &link_dest) {
            println!("  ⚠️ Peringatan Workspace: Gagal OS Symlink untuk {}. Harus admin.", local_pkg.name);
            println!("  💡 Beralih ke Omni Internal Memory Router . Error: {}", e);
            // Internal router fallback will be handled by the compiler logic
        }

        Ok(())
    }
}
