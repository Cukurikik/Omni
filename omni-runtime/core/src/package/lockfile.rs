// ============================================================
// 🔒 OMNI Lockfile — omni.lock Generator & Parser
// ============================================================
// Menghasilkan lockfile deterministik untuk build reproducible.
// Setara dengan package-lock.json di npm.
// ============================================================

use std::collections::HashMap;
use std::path::Path;
use std::fs;

use super::resolver::ResolvedPackage;

/// Satu entri dalam lockfile
#[derive(Debug, Clone)]
pub struct LockEntry {
    pub name: String,
    pub version: String,
    pub checksum: String,
    pub source: String,
    pub is_dev: bool,
    pub depends: Vec<String>,
}

/// Lockfile lengkap
#[derive(Debug)]
pub struct OmniLockfile {
    pub version: u32,
    pub generated_by: String,
    pub generated_at: String,
    pub entries: Vec<LockEntry>,
}

impl OmniLockfile {
    /// Generate lockfile baru dari hasil resolusi
    pub fn from_resolved(packages: &[ResolvedPackage]) -> Self {
        let entries: Vec<LockEntry> = packages
            .iter()
            .map(|pkg| {
                // Generate checksum placeholder (di produksi: hash konten paket)
                let checksum = format!(
                    "sha256:{}",
                    Self::simple_hash(&format!("{}@{}", pkg.name, pkg.version))
                );

                let source = match &pkg.source {
                    super::manifest::DependencySource::Builtin => "builtin".to_string(),
                    super::manifest::DependencySource::Registry(url) => format!("registry:{}", url),
                    super::manifest::DependencySource::Git { url, branch } => {
                        format!("git:{}#{}", url, branch.as_deref().unwrap_or("main"))
                    }
                    super::manifest::DependencySource::Local(path) => {
                        format!("local:{}", path.display())
                    }
                };

                let depends: Vec<String> = pkg.transitive_deps
                    .iter()
                    .map(|d| format!("{}@*", d))
                    .collect();

                LockEntry {
                    name: pkg.name.clone(),
                    version: pkg.version.clone(),
                    checksum,
                    source,
                    is_dev: pkg.is_dev,
                    depends,
                }
            })
            .collect();

        OmniLockfile {
            version: 1,
            generated_by: "omni-cli v1.0.0".to_string(),
            generated_at: chrono_now(),
            entries,
        }
    }

    /// Serialize lockfile ke format TOML
    pub fn to_toml(&self) -> String {
        let mut output = String::new();
        
        output.push_str("# ============================================================\n");
        output.push_str("# omni.lock — OMNI Dependency Lockfile\n");
        output.push_str("# ============================================================\n");
        output.push_str("# JANGAN EDIT FILE INI SECARA MANUAL.\n");
        output.push_str("# File ini di-generate otomatis oleh `omni install` atau `omni get`.\n");
        output.push_str("# Commit file ini ke Git untuk build yang deterministik.\n");
        output.push_str("# ============================================================\n\n");
        
        output.push_str("[metadata]\n");
        output.push_str(&format!("generated_by = \"{}\"\n", self.generated_by));
        output.push_str(&format!("generated_at = \"{}\"\n", self.generated_at));
        output.push_str(&format!("lockfile_version = {}\n", self.version));
        output.push('\n');
        
        output.push_str("# ─── Resolved Dependencies ─────────────────────────────────\n\n");
        
        for entry in &self.entries {
            output.push_str("[[package]]\n");
            output.push_str(&format!("name     = \"{}\"\n", entry.name));
            output.push_str(&format!("version  = \"{}\"\n", entry.version));
            output.push_str(&format!("checksum = \"{}\"\n", entry.checksum));
            output.push_str(&format!("source   = \"{}\"\n", entry.source));
            
            if entry.is_dev {
                output.push_str("dev      = true\n");
            }
            
            if !entry.depends.is_empty() {
                output.push_str(&format!(
                    "depends  = [{}]\n",
                    entry.depends.iter()
                        .map(|d| format!("\"{}\"", d))
                        .collect::<Vec<_>>()
                        .join(", ")
                ));
            }
            
            output.push('\n');
        }
        
        output
    }

    /// Tulis lockfile ke disk
    pub fn write_to(&self, project_dir: &Path) -> std::io::Result<()> {
        let lock_path = project_dir.join("omni.lock");
        let content = self.to_toml();
        fs::write(&lock_path, &content)?;
        println!("🔒 [LOCKFILE] omni.lock ditulis ({} paket)", self.entries.len());
        Ok(())
    }

    /// Parse lockfile yang sudah ada
    pub fn from_file(project_dir: &Path) -> Option<Self> {
        let lock_path = project_dir.join("omni.lock");
        
        if !lock_path.exists() {
            return None;
        }

        let content = fs::read_to_string(&lock_path).ok()?;
        let doc: toml::Value = content.parse().ok()?;
        let table = doc.as_table()?;

        // Parse metadata
        let meta = table.get("metadata")?.as_table()?;
        let generated_by = meta.get("generated_by")?.as_str()?.to_string();
        let generated_at = meta.get("generated_at")?.as_str()?.to_string();
        let version = meta.get("lockfile_version")?.as_integer()? as u32;

        // Parse packages
        let packages = table.get("package")?.as_array()?;
        let entries: Vec<LockEntry> = packages
            .iter()
            .filter_map(|pkg| {
                let t = pkg.as_table()?;
                Some(LockEntry {
                    name: t.get("name")?.as_str()?.to_string(),
                    version: t.get("version")?.as_str()?.to_string(),
                    checksum: t.get("checksum")?.as_str()?.to_string(),
                    source: t.get("source")?.as_str()?.to_string(),
                    is_dev: t.get("dev").and_then(|v| v.as_bool()).unwrap_or(false),
                    depends: t.get("depends")
                        .and_then(|v| v.as_array())
                        .map(|arr| {
                            arr.iter()
                                .filter_map(|v| v.as_str().map(|s| s.to_string()))
                                .collect()
                        })
                        .unwrap_or_default(),
                })
            })
            .collect();

        Some(OmniLockfile {
            version,
            generated_by,
            generated_at,
            entries,
        })
    }

    /// Cek apakah lockfile masih sinkron dengan manifest
    pub fn is_in_sync(&self, dep_names: &[String]) -> bool {
        let locked_names: HashMap<&str, &LockEntry> = self.entries
            .iter()
            .map(|e| (e.name.as_str(), e))
            .collect();
        
        for name in dep_names {
            if !locked_names.contains_key(name.as_str()) {
                return false;
            }
        }
        true
    }

    /// Simple hash function (placeholder — di produksi gunakan Blake3)
    fn simple_hash(input: &str) -> String {
        let mut hash: u64 = 5381;
        for byte in input.bytes() {
            hash = hash.wrapping_mul(33).wrapping_add(byte as u64);
        }
        format!("{:016x}{:016x}{:016x}{:016x}", hash, hash ^ 0xDEAD, hash ^ 0xBEEF, hash ^ 0xCAFE)
    }
}

/// Dapatkan waktu saat ini sebagai ISO-8601 string
fn chrono_now() -> String {
    // Tanpa dependensi chrono — gunakan SystemTime
    use std::time::{SystemTime, UNIX_EPOCH};
    let secs = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs();
    
    // Konversi sederhana ke format readable
    let days = secs / 86400;
    let years = 1970 + days / 365;
    let rem_days = days % 365;
    let months = rem_days / 30 + 1;
    let day = rem_days % 30 + 1;
    let hours = (secs % 86400) / 3600;
    let mins = (secs % 3600) / 60;
    let sec = secs % 60;
    
    format!("{:04}-{:02}-{:02}T{:02}:{:02}:{:02}Z", years, months, day, hours, mins, sec)
}

#[cfg(test)]
mod tests {
    use super::*;
    use super::super::manifest::DependencySource;

    #[test]
    fn test_lockfile_generation() {
        let packages = vec![
            ResolvedPackage {
                name: "omni-std".to_string(),
                version: "1.0.0".to_string(),
                source: DependencySource::Builtin,
                is_dev: false,
                install_path: std::path::PathBuf::from("omni_modules/omni-std"),
                transitive_deps: vec![],
            },
            ResolvedPackage {
                name: "omni-test".to_string(),
                version: "1.0.0".to_string(),
                source: DependencySource::Builtin,
                is_dev: true,
                install_path: std::path::PathBuf::from("omni_modules/omni-test"),
                transitive_deps: vec!["omni-std".to_string()],
            },
        ];

        let lockfile = OmniLockfile::from_resolved(&packages);
        assert_eq!(lockfile.entries.len(), 2);
        assert_eq!(lockfile.entries[0].name, "omni-std");
        assert!(!lockfile.entries[0].is_dev);
        assert!(lockfile.entries[1].is_dev);
        
        let toml = lockfile.to_toml();
        assert!(toml.contains("omni-std"));
        assert!(toml.contains("omni-test"));
        assert!(toml.contains("dev      = true"));
    }

    #[test]
    fn test_is_in_sync() {
        let lockfile = OmniLockfile {
            version: 1,
            generated_by: "test".to_string(),
            generated_at: "now".to_string(),
            entries: vec![
                LockEntry {
                    name: "omni-std".to_string(),
                    version: "1.0.0".to_string(),
                    checksum: "sha256:abc".to_string(),
                    source: "builtin".to_string(),
                    is_dev: false,
                    depends: vec![],
                },
            ],
        };

        assert!(lockfile.is_in_sync(&["omni-std".to_string()]));
        assert!(!lockfile.is_in_sync(&["omni-std".to_string(), "omni-net".to_string()]));
    }
}
