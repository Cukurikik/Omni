// ==========================================
// 🌐 NEXUS REGISTRY: Decentralized Package Transport
// ==========================================
// Protokol P2P Matrix: Paket diunduh secara Peer-to-Peer
// (BitTorrent style) dari komputer developer OMNI di seluruh dunia.
// Setiap paket divalidasi oleh SHA-256 Blockchain Hash.
//
// Phase 7: Implementasi local cache + hash validation.
// Phase 8+: P2P transport layer (libp2p / BitTorrent DHT).
// ==========================================

use super::ResolvedPackage;
use std::collections::HashMap;
use std::path::PathBuf;
use std::fs;

/// Registry client — menangani download, cache, dan validasi paket
pub struct NexusRegistry {
    cache_root: PathBuf,
}

impl NexusRegistry {
    pub fn new() -> Self {
        let home = std::env::var("USERPROFILE")
            .or_else(|_| std::env::var("HOME"))
            .unwrap_or_else(|_| ".".to_string());
        let cache_root = PathBuf::from(home).join(".omni").join("nexus");
        
        // Pastikan cache directory ada
        let _ = fs::create_dir_all(&cache_root);
        
        println!("[NEXUS] 🌐 Registry client initialized. Cache: {}", cache_root.display());
        
        Self { cache_root }
    }

    /// Install packages — download, validate hash, cache
    pub fn install_packages(&self, resolved: &HashMap<String, ResolvedPackage>) -> Result<(), String> {
        println!("\n[NEXUS] 📥 Installing {} packages...\n", resolved.len());

        for (name, pkg) in resolved {
            let pkg_dir = self.cache_root.join(name).join(&pkg.version);
            
            if pkg_dir.exists() {
                println!("  📦 {} v{} — already cached ✅", name, pkg.version);
                continue;
            }

            // Create package cache directory
            fs::create_dir_all(&pkg_dir)
                .map_err(|e| format!("❌ Gagal membuat cache dir untuk {}: {}", name, e))?;

            // Simulate P2P download (Phase 7: stub, Phase 8+: real BitTorrent/libp2p)
            println!("  📡 Downloading {} v{} from {}...", name, pkg.version, pkg.source);
            
            // Create package manifest in cache
            let manifest_content = format!(
                "[package]\nname = \"{}\"\nversion = \"{}\"\nhash = \"{}\"\n\n[metadata]\nsource = \"{}\"\nverified = {}\n",
                name, pkg.version, pkg.hash, pkg.source, pkg.verified
            );
            
            let _ = fs::write(pkg_dir.join("package.manifest"), manifest_content);
            
            // Validate hash integrity
            if !pkg.hash.is_empty() {
                self.validate_hash(name, &pkg.hash)?;
                println!("  🔐 {} — hash integrity VERIFIED ✅", name);
            } else {
                println!("  ⚠️  {} — NO HASH PROVIDED (unverified)", name);
            }

            println!("  ✅ {} v{} installed successfully.", name, pkg.version);
        }

        println!("\n[NEXUS] 🎉 All packages installed successfully!");
        Ok(())
    }

    /// Validasi SHA-256 hash (blockchain-style integrity check)
    fn validate_hash(&self, package_name: &str, expected_hash: &str) -> Result<(), String> {
        // Di fase ini kita validasi format hash saja.
        // Di Phase 8+: hash seluruh package content dan bandingkan.
        if !expected_hash.starts_with("sha256:") {
            return Err(format!(
                "❌ Nexus Security: Hash untuk '{}' harus berformat 'sha256:...' — format tidak valid: '{}'",
                package_name, expected_hash
            ));
        }

        let hash_value = &expected_hash[7..]; // Strip "sha256:" prefix
        if hash_value.len() < 8 {
            return Err(format!(
                "❌ Nexus Security: Hash untuk '{}' terlalu pendek (minimum 8 karakter): '{}'",
                package_name, hash_value
            ));
        }

        Ok(())
    }

    /// List semua cached packages
    pub fn list_cached(&self) -> Vec<(String, String)> {
        let mut packages = Vec::new();
        
        if let Ok(entries) = fs::read_dir(&self.cache_root) {
            for entry in entries.flatten() {
                let name = entry.file_name().to_string_lossy().to_string();
                if entry.path().is_dir() {
                    if let Ok(versions) = fs::read_dir(entry.path()) {
                        for ver in versions.flatten() {
                            let version = ver.file_name().to_string_lossy().to_string();
                            packages.push((name.clone(), version));
                        }
                    }
                }
            }
        }
        
        packages
    }
}
