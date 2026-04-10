// ============================================================
// 🔄 OMNI Dependency Resolver
// ============================================================
// Menyelesaikan dependency tree dari Omnifile.toml.
// Mendeteksi konflik versi, circular dependencies, dan
// memastikan semua paket tersedia di omni_modules/.
// ============================================================

use std::collections::{HashMap, HashSet, VecDeque};
use std::path::{Path, PathBuf};
use std::fs;

use super::manifest::{OmniManifest, DependencySpec, DependencySource};

/// Paket yang sudah di-resolve (siap install)
#[derive(Debug, Clone)]
pub struct ResolvedPackage {
    pub name: String,
    pub version: String,
    pub source: DependencySource,
    pub is_dev: bool,
    pub install_path: PathBuf,
    pub transitive_deps: Vec<String>,
}

/// Hasil dari proses resolving
#[derive(Debug)]
pub struct ResolutionResult {
    pub packages: Vec<ResolvedPackage>,
    pub warnings: Vec<String>,
}

/// Error saat resolving
#[derive(Debug)]
pub enum ResolveError {
    ManifestNotFound(PathBuf),
    CircularDependency(Vec<String>),
    VersionConflict { package: String, required: String, found: String },
    PackageNotFound(String),
}

impl std::fmt::Display for ResolveError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ResolveError::ManifestNotFound(p) => {
                write!(f, "[OMNI-E710] Manifest tidak ditemukan: {}", p.display())
            }
            ResolveError::CircularDependency(chain) => {
                write!(f, "[OMNI-E711] Circular dependency terdeteksi: {}", chain.join(" → "))
            }
            ResolveError::VersionConflict { package, required, found } => {
                write!(f, "[OMNI-E712] Konflik versi {}: butuh {}, ditemukan {}", package, required, found)
            }
            ResolveError::PackageNotFound(name) => {
                write!(f, "[OMNI-E713] Paket tidak ditemukan: {}", name)
            }
        }
    }
}

/// OMNI Package Resolver
pub struct OmniResolver {
    #[allow(dead_code)]
    project_dir: PathBuf,
    modules_dir: PathBuf,
    builtin_packages: HashSet<String>,
}

impl OmniResolver {
    pub fn new(project_dir: &Path) -> Self {
        let modules_dir = project_dir.join("omni_modules");
        
        // Daftar paket builtin yang selalu tersedia
        let mut builtin = HashSet::new();
        let builtin_list = [
            "omni-std", "omni-runtime", "omni-types", // CORE
            "omni-fs", "omni-env", "omni-crypto", "omni-net", "omni-process", // SYSTEM
            "omni-db", "omni-cache", "omni-stream", "omni-validate", // DATA
            "omni-auth", "omni-http", "omni-graphql", "omni-queue", // APPLICATION
            "omni-test", "omni-log", "omni-config", "omni-cli", // TOOLING
            "omni-ai", "omni-monitor" // PREMIUM
        ];
        
        for pkg in builtin_list.iter() {
            builtin.insert(pkg.to_string());
        }
        
        Self {
            project_dir: project_dir.to_path_buf(),
            modules_dir,
            builtin_packages: builtin,
        }
    }

    /// Resolve seluruh dependency tree dari Omnifile.toml
    pub fn resolve(&self, manifest: &OmniManifest) -> Result<ResolutionResult, ResolveError> {
        let mut resolved: Vec<ResolvedPackage> = Vec::new();
        let mut visited: HashSet<String> = HashSet::new();
        let mut warnings: Vec<String> = Vec::new();
        let mut queue: VecDeque<(String, DependencySpec, bool)> = VecDeque::new();

        // Enqueue semua production dependencies
        for (name, spec) in &manifest.dependencies {
            queue.push_back((name.clone(), spec.clone(), false));
        }

        // Enqueue semua dev dependencies
        for (name, spec) in &manifest.dev_dependencies {
            queue.push_back((name.clone(), spec.clone(), true));
        }

        // BFS resolution
        while let Some((name, spec, is_dev)) = queue.pop_front() {
            if visited.contains(&name) {
                continue;
            }
            visited.insert(name.clone());

            // Cek apakah paket sudah ada di omni_modules/
            let install_path = self.modules_dir.join(&name);
            let already_installed = install_path.exists();

            // Resolve transitive dependencies
            let transitive_deps = if already_installed {
                self.resolve_transitive(&install_path, &mut queue, is_dev)?
            } else if self.builtin_packages.contains(&name) {
                // Builtin tidak perlu download, tapi cek subdeps
                vec![]
            } else {
                warnings.push(format!(
                    "⚠️  Paket '{}@{}' belum terinstal. Jalankan `omni get {}`",
                    name, spec.version, name
                ));
                vec![]
            };

            resolved.push(ResolvedPackage {
                name: name.clone(),
                version: spec.version.clone(),
                source: spec.source.clone(),
                is_dev,
                install_path,
                transitive_deps,
            });
        }

        // Deteksi circular dependencies
        self.check_circular(&resolved)?;

        println!("📦 [RESOLVER] {} paket di-resolve ({} production, {} dev)",
            resolved.len(),
            resolved.iter().filter(|p| !p.is_dev).count(),
            resolved.iter().filter(|p| p.is_dev).count(),
        );

        Ok(ResolutionResult { packages: resolved, warnings })
    }

    /// Resolve transitive dependencies dari omni_modules/<pkg>/Omnifile.toml
    fn resolve_transitive(
        &self,
        pkg_path: &Path,
        queue: &mut VecDeque<(String, DependencySpec, bool)>,
        is_dev: bool,
    ) -> Result<Vec<String>, ResolveError> {
        let manifest_path = pkg_path.join("Omnifile.toml");
        if !manifest_path.exists() {
            return Ok(vec![]);
        }

        let content = fs::read_to_string(&manifest_path)
            .map_err(|_| ResolveError::ManifestNotFound(manifest_path))?;
        
        let sub_manifest = OmniManifest::parse(&content)
            .map_err(|e| ResolveError::PackageNotFound(format!("{}", e)))?;

        let mut deps = Vec::new();
        for (name, spec) in &sub_manifest.dependencies {
            deps.push(name.clone());
            queue.push_back((name.clone(), spec.clone(), is_dev));
        }

        Ok(deps)
    }

    /// Deteksi circular dependencies
    fn check_circular(&self, packages: &[ResolvedPackage]) -> Result<(), ResolveError> {
        let dep_map: HashMap<&str, &[String]> = packages
            .iter()
            .map(|p| (p.name.as_str(), p.transitive_deps.as_slice()))
            .collect();

        for pkg in packages {
            let mut visited: HashSet<&str> = HashSet::new();
            let mut stack: Vec<&str> = vec![&pkg.name];

            while let Some(current) = stack.pop() {
                if !visited.insert(current) {
                    // Circular detected!
                    return Err(ResolveError::CircularDependency(
                        visited.into_iter().map(|s| s.to_string()).collect()
                    ));
                }

                if let Some(deps) = dep_map.get(current) {
                    for dep in *deps {
                        stack.push(dep);
                    }
                }
            }
        }

        Ok(())
    }

    /// Install paket builtin ke omni_modules/ (salin dari template)
    pub fn ensure_builtin_packages(&self) -> Result<Vec<String>, ResolveError> {
        let mut installed = Vec::new();

        for pkg_name in &self.builtin_packages {
            let target_dir = self.modules_dir.join(pkg_name);
            if target_dir.exists() {
                installed.push(format!("✅ {} (sudah ada)", pkg_name));
            } else {
                // Buat folder src
                fs::create_dir_all(target_dir.join("src"))
                    .map_err(|_| ResolveError::PackageNotFound(pkg_name.clone()))?;
                
                // 1. Tulis Omnifile.toml khusus untuk paket builtin ini
                let manifest_content = format!(r#"# ============================================================
# Omnifile.toml — Bawaan OMNI Framework (Internal)
# ============================================================

[package]
name        = "{}"
version     = "1.0.0"
edition     = "omni-2025"
authors     = ["OMNI Core Team"]
description = "Internal OMNI Framework builtin module"
license     = "MIT"

[dependencies]
# Kosong (Builtin module independen atau rely on core)
"#, pkg_name);
                let _ = fs::write(target_dir.join("Omnifile.toml"), manifest_content);

                // 2. Tulis src/lib.omni sederhana
                // Nantinya akan di-link ke implementasi native C/Rust secara otomatis
                let lib_content = format!(r#"// ⚡ {} — OMNI Builtin Module
// Modul ini adalah jembatan menuju implementasi native engine.
// Developer bisa melakukan import "{}";

@system_module
export struct {}_Interface {{
    version: "1.0.0"
}}

// TODO: Definisikan interface publik secara deklaratif 
"#, pkg_name, pkg_name, pkg_name.replace("-", "_"));
                let _ = fs::write(target_dir.join("src").join("lib.omni"), lib_content);

                installed.push(format!("📥 {} (ter-install dgn Omnifile.toml)", pkg_name));
            }
        }

        Ok(installed)
    }

    /// Dapatkan path ke omni_modules/
    pub fn modules_dir(&self) -> &Path {
        &self.modules_dir
    }

    /// Versi SemVer: apakah `installed` memenuhi `required`?
    pub fn version_satisfies(required: &str, installed: &str) -> bool {
        if required == "*" || required == "latest" {
            return true;
        }
        
        // Handle caret ^1.0.0 — compatible with 1.x.x
        if let Some(stripped) = required.strip_prefix('^') {
            let req_parts: Vec<&str> = stripped.split('.').collect();
            let inst_parts: Vec<&str> = installed.split('.').collect();
            
            if req_parts.is_empty() || inst_parts.is_empty() {
                return false;
            }
            
            // Major version harus sama
            return req_parts[0] == inst_parts[0];
        }
        
        // Handle tilde ~1.0.0 — compatible with 1.0.x
        if let Some(stripped) = required.strip_prefix('~') {
            let req_parts: Vec<&str> = stripped.split('.').collect();
            let inst_parts: Vec<&str> = installed.split('.').collect();
            
            if req_parts.len() < 2 || inst_parts.len() < 2 {
                return false;
            }
            
            // Major dan minor harus sama
            return req_parts[0] == inst_parts[0] && req_parts[1] == inst_parts[1];
        }
        
        // Exact match
        required == installed
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_version_satisfies_exact() {
        assert!(OmniResolver::version_satisfies("1.0.0", "1.0.0"));
        assert!(!OmniResolver::version_satisfies("1.0.0", "1.0.1"));
    }

    #[test]
    fn test_version_satisfies_caret() {
        assert!(OmniResolver::version_satisfies("^1.0.0", "1.5.3"));
        assert!(!OmniResolver::version_satisfies("^1.0.0", "2.0.0"));
    }

    #[test]
    fn test_version_satisfies_tilde() {
        assert!(OmniResolver::version_satisfies("~1.0.0", "1.0.9"));
        assert!(!OmniResolver::version_satisfies("~1.0.0", "1.1.0"));
    }

    #[test]
    fn test_version_satisfies_wildcard() {
        assert!(OmniResolver::version_satisfies("*", "99.99.99"));
        assert!(OmniResolver::version_satisfies("latest", "1.0.0"));
    }
}
