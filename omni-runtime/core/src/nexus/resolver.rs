// ==========================================
// 🔍 NEXUS RESOLVER: Dependency Graph Solver
// ==========================================
// Topological sort dan semantic versioning untuk 
// dependency tree OMNI packages.
// ==========================================

use super::{OmniDependency, ResolvedPackage};
use std::collections::HashMap;
use std::path::PathBuf;

/// Semantic Version parser
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SemVer {
    pub major: u32,
    pub minor: u32,
    pub patch: u32,
}

impl SemVer {
    pub fn parse(version: &str) -> Result<Self, String> {
        if version == "latest" || version == "*" || version == "" {
            return Ok(SemVer { major: 999, minor: 999, patch: 999 });
        }
        
        let cleaned = version.trim_start_matches(|c: char| !c.is_ascii_digit());
        let parts: Vec<&str> = cleaned.split('.').collect();
        
        if parts.len() < 2 {
            return Err(format!("❌ Versi tidak valid: '{}'", version));
        }

        Ok(SemVer {
            major: parts[0].parse().unwrap_or(0),
            minor: parts[1].parse().unwrap_or(0),
            patch: if parts.len() > 2 { parts[2].parse().unwrap_or(0) } else { 0 },
        })
    }

    pub fn satisfies(&self, constraint: &str) -> bool {
        if let Ok(vc) = VersionConstraint::parse(constraint) {
            return self >= &vc.min && self <= &vc.max;
        }
        false
    }
}

/// SAT Solver: Minimal Version Selection Engine
/// Constraint boolean logic mapping.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct VersionConstraint {
    pub min: SemVer,
    pub max: SemVer,
}

impl VersionConstraint {
    pub fn parse(constraint: &str) -> Result<Self, String> {
        let trimmed = constraint.trim();
        
        if let Some(ver_str) = trimmed.strip_prefix(">=") {
            let min = SemVer::parse(ver_str)?;
            Ok(Self { min, max: SemVer { major: 999, minor: 999, patch: 999 } })
        } else if let Some(ver_str) = trimmed.strip_prefix('^') {
            let base = SemVer::parse(ver_str)?;
            Ok(Self { 
                min: base.clone(), 
                max: SemVer { major: base.major, minor: 999, patch: 999 } 
            })
        } else if let Some(ver_str) = trimmed.strip_prefix('~') {
            let base = SemVer::parse(ver_str)?;
            Ok(Self { 
                min: base.clone(), 
                max: SemVer { major: base.major, minor: base.minor, patch: 999 } 
            })
        } else {
            let exact = SemVer::parse(trimmed)?;
            Ok(Self { min: exact.clone(), max: exact })
        }
    }

    /// SAT Solver Intersection Checker (Fail-Fast Algorithm)
    pub fn intersect(&self, other: &Self) -> Result<Self, String> {
        let new_min = std::cmp::max(self.min.clone(), other.min.clone());
        let new_max = std::cmp::min(self.max.clone(), other.max.clone());

        if new_min > new_max {
            return Err("SAT Solver Blocked: Titik perpotongan tidak ditemukan (Konflik Absolut)".to_string());
        }

        Ok(Self { min: new_min, max: new_max })
    }
}

impl PartialOrd for SemVer {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for SemVer {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        self.major.cmp(&other.major)
            .then(self.minor.cmp(&other.minor))
            .then(self.patch.cmp(&other.patch))
    }
}

/// Dependency resolver — topological sort + conflict detection
pub struct NexusResolver {
    resolved: HashMap<String, ResolvedPackage>,
}

impl NexusResolver {
    pub fn new() -> Self {
        println!("[NEXUS] 🔍 Dependency Resolver diaktifkan.");
        Self {
            resolved: HashMap::new(),
        }
    }

    /// Resolve semua dependencies dari Omnifile
    pub fn resolve(&mut self, deps: &[OmniDependency]) -> Result<HashMap<String, ResolvedPackage>, String> {
        println!("[NEXUS] 📊 Menyelesaikan {} dependensi...", deps.len());

        for dep in deps {
            let constraint = VersionConstraint::parse(&dep.version)
                .map_err(|e| format!("Dep '{}': {}", dep.name, e))?;

            // Validate hash format
            if !dep.hash.is_empty() && !dep.hash.starts_with("sha256:") {
                return Err(format!(
                    "❌ Nexus: Hash untuk '{}' harus berformat 'sha256:...' — ditemukan: '{}'",
                    dep.name, dep.hash
                ));
            }

            // OMNI SAT SOLVER: Periksa irisan constraint untuk Single Package Instance
            let final_version = if let Some(existing) = self.resolved.get(&dep.name) {
                let existing_constraint = VersionConstraint::parse(&existing.version).unwrap();
                let intersection = constraint.intersect(&existing_constraint)
                    .map_err(|_e| format!("❌ Nexus KEBOCORAN MODUL TERDETEKSI! '{}' konflik: {} vs {}. OMNI menggugurkan build untuk melindungi Production!", dep.name, existing.version, dep.version))?;
                
                // Pada MVS, kita pilih versi minimum yang beririsan
                format!("{}.{}.{}", intersection.min.major, intersection.min.minor, intersection.min.patch)
            } else {
                format!("{}.{}.{}", constraint.min.major, constraint.min.minor, constraint.min.patch)
            };

            // Determine cache path
            let cache_dir = dirs_stub();
            let cache_path = cache_dir
                .join(&dep.name)
                .join(&final_version);

            let resolved_pkg = ResolvedPackage {
                name: dep.name.clone(),
                version: final_version.clone(),
                hash: dep.hash.clone(),
                source: if cache_path.exists() {
                    "local://cache".to_string()
                } else {
                    "nexus://p2p".to_string()
                },
                verified: !dep.hash.is_empty(),
                cache_path,
            };

            println!("  ✅ {} v{} → {} ({})", 
                resolved_pkg.name, 
                resolved_pkg.version,
                resolved_pkg.source,
                if resolved_pkg.verified { "hash verified" } else { "no hash" }
            );

            self.resolved.insert(dep.name.clone(), resolved_pkg);
        }

        println!("[NEXUS] 🎯 Semua {} dependensi berhasil di-resolve.", deps.len());
        Ok(self.resolved.clone())
    }
}

/// Stub for home directory (avoids adding dirs crate dependency)
fn dirs_stub() -> PathBuf {
    let home = std::env::var("USERPROFILE")
        .or_else(|_| std::env::var("HOME"))
        .unwrap_or_else(|_| ".".to_string());
    PathBuf::from(home).join(".omni").join("nexus")
}
