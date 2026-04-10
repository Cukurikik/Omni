// ============================================================
// 📄 OMNI Manifest Parser — Omnifile.toml
// ============================================================
// Mem-parse Omnifile.toml menjadi struct Rust yang typed.
// Setara dengan cara npm membaca package.json.
// ============================================================

use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::fs;

/// Representasi lengkap dari Omnifile.toml
#[derive(Debug, Clone)]
pub struct OmniManifest {
    pub package: PackageInfo,
    pub dependencies: HashMap<String, DependencySpec>,
    pub dev_dependencies: HashMap<String, DependencySpec>,
    pub scripts: HashMap<String, String>,
    pub permissions: PermissionSet,
    pub build: BuildConfig,
}

/// Metadata paket
#[derive(Debug, Clone)]
pub struct PackageInfo {
    pub name: String,
    pub version: String,
    pub edition: String,
    pub authors: Vec<String>,
    pub description: String,
    pub license: String,
    pub homepage: String,
    pub repository: String,
    pub keywords: Vec<String>,
}

/// Spesifikasi dependency — versi, source, fitur
#[derive(Debug, Clone)]
pub struct DependencySpec {
    pub name: String,
    pub version: String,
    pub source: DependencySource,
    pub features: Vec<String>,
}

/// Dari mana paket diambil
#[derive(Debug, Clone)]
pub enum DependencySource {
    /// Paket bawaan yang disertakan dengan OMNI
    Builtin,
    /// Dari OMNI-NEXUS registry
    Registry(String),
    /// Dari Git repository
    Git { url: String, branch: Option<String> },
    /// Dari path lokal
    Local(PathBuf),
}

/// Izin yang dibutuhkan oleh proyek
#[derive(Debug, Clone)]
pub struct PermissionSet {
    pub allow_net: Vec<String>,
    pub allow_fs: Vec<String>,
    pub allow_env: Vec<String>,
    pub allow_thread: bool,
    pub allow_eval: bool,
}

/// Konfigurasi build
#[derive(Debug, Clone)]
pub struct BuildConfig {
    pub target: Vec<String>,
    pub optimize: String,
    pub entry_point: String,
}

/// Error saat parsing manifest
#[derive(Debug)]
pub enum ManifestError {
    FileNotFound(PathBuf),
    ParseError(String),
    MissingField(String),
}

impl std::fmt::Display for ManifestError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ManifestError::FileNotFound(path) => {
                write!(f, "[OMNI-E700] Omnifile.toml tidak ditemukan: {}", path.display())
            }
            ManifestError::ParseError(msg) => {
                write!(f, "[OMNI-E701] Gagal parse Omnifile.toml: {}", msg)
            }
            ManifestError::MissingField(field) => {
                write!(f, "[OMNI-E702] Field wajib tidak ada: {}", field)
            }
        }
    }
}

impl OmniManifest {
    /// Cari dan parse Omnifile.toml dari direktori proyek.
    pub fn from_dir(project_dir: &Path) -> Result<Self, ManifestError> {
        let manifest_path = project_dir.join("Omnifile.toml");
        
        if !manifest_path.exists() {
            return Err(ManifestError::FileNotFound(manifest_path));
        }
        
        let content = fs::read_to_string(&manifest_path)
            .map_err(|e| ManifestError::ParseError(format!("IO error: {}", e)))?;
        
        Self::parse(&content)
    }

    /// Parse string TOML menjadi OmniManifest.
    pub fn parse(content: &str) -> Result<Self, ManifestError> {
        let doc: toml::Table = content.parse()
            .map_err(|e: toml::de::Error| ManifestError::ParseError(e.to_string()))?;
        
        // Parse [package]
        let pkg_table = doc.get("package")
            .and_then(|v| v.as_table())
            .ok_or_else(|| ManifestError::MissingField("[package]".into()))?;
        
        let package = PackageInfo {
            name: get_string(pkg_table, "name")
                .ok_or_else(|| ManifestError::MissingField("package.name".into()))?,
            version: get_string(pkg_table, "version").unwrap_or_else(|| "0.1.0".into()),
            edition: get_string(pkg_table, "edition").unwrap_or_else(|| "omni-2025".into()),
            authors: get_string_array(pkg_table, "authors"),
            description: get_string(pkg_table, "description").unwrap_or_default(),
            license: get_string(pkg_table, "license").unwrap_or_else(|| "MIT".into()),
            homepage: get_string(pkg_table, "homepage").unwrap_or_default(),
            repository: get_string(pkg_table, "repository").unwrap_or_default(),
            keywords: get_string_array(pkg_table, "keywords"),
        };

        // Parse [dependencies]
        let dependencies = parse_deps(doc.get("dependencies"));
        
        // Parse [dev-dependencies]
        let dev_dependencies = parse_deps(doc.get("dev-dependencies"));

        // Parse [scripts]
        let scripts = doc.get("scripts")
            .and_then(|v: &toml::Value| v.as_table())
            .map(|t| {
                t.iter()
                    .filter_map(|(k, v)| v.as_str().map(|s| (k.clone(), s.to_string())))
                    .collect()
            })
            .unwrap_or_default();

        // Parse [permissions]
        let perm_table = doc.get("permissions").and_then(|v: &toml::Value| v.as_table());
        let permissions = PermissionSet {
            allow_net: perm_table.map(|t| get_string_array(t, "allow_net")).unwrap_or_default(),
            allow_fs: perm_table.map(|t| get_string_array(t, "allow_fs")).unwrap_or_default(),
            allow_env: perm_table.map(|t| get_string_array(t, "allow_env")).unwrap_or_default(),
            allow_thread: perm_table
                .and_then(|t| t.get("allow_thread"))
                .and_then(|v: &toml::Value| v.as_bool())
                .unwrap_or(false),
            allow_eval: perm_table
                .and_then(|t| t.get("allow_eval"))
                .and_then(|v: &toml::Value| v.as_bool())
                .unwrap_or(false),
        };

        // Parse [build]
        let build_table = doc.get("build").and_then(|v: &toml::Value| v.as_table());
        let build = BuildConfig {
            target: build_table.map(|t| get_string_array(t, "target")).unwrap_or_default(),
            optimize: build_table
                .and_then(|t| get_string(t, "optimize"))
                .unwrap_or_else(|| "debug".into()),
            entry_point: build_table
                .and_then(|t| get_string(t, "entry_point"))
                .unwrap_or_else(|| "src/main.omni".into()),
        };

        Ok(OmniManifest {
            package,
            dependencies,
            dev_dependencies,
            scripts,
            permissions,
            build,
        })
    }

    /// Dapatkan semua dependency (termasuk dev).
    pub fn all_dependencies(&self) -> HashMap<String, DependencySpec> {
        let mut all = self.dependencies.clone();
        all.extend(self.dev_dependencies.clone());
        all
    }

    /// Cek apakah suatu paket ada di dependency list.
    pub fn has_dependency(&self, name: &str) -> bool {
        self.dependencies.contains_key(name) || self.dev_dependencies.contains_key(name)
    }
}

// ─── Helper Functions ─────────────────────────────────────

fn get_string(table: &toml::map::Map<String, toml::Value>, key: &str) -> Option<String> {
    table.get(key).and_then(|v| v.as_str()).map(|s| s.to_string())
}

fn get_string_array(table: &toml::map::Map<String, toml::Value>, key: &str) -> Vec<String> {
    table.get(key)
        .and_then(|v| v.as_array())
        .map(|arr| {
            arr.iter()
                .filter_map(|v| v.as_str().map(|s| s.to_string()))
                .collect()
        })
        .unwrap_or_default()
}

fn parse_deps(deps_value: Option<&toml::Value>) -> HashMap<String, DependencySpec> {
    let mut map = HashMap::new();
    
    if let Some(table) = deps_value.and_then(|v| v.as_table()) {
        for (name, value) in table {
            let spec = match value {
                // Versi sederhana: omni-std = "1.0.0"
                toml::Value::String(version) => DependencySpec {
                    name: name.clone(),
                    version: version.clone(),
                    source: DependencySource::Builtin,
                    features: vec![],
                },
                // Spesifikasi lengkap: omni-net = { version = "1.0.0", features = ["http2"] }
                toml::Value::Table(spec_table) => {
                    let version = get_string(spec_table, "version")
                        .unwrap_or_else(|| "*".into());
                    let features = get_string_array(spec_table, "features");
                    
                    let source = if let Some(git_url) = get_string(spec_table, "git") {
                        let branch = get_string(spec_table, "branch");
                        DependencySource::Git { url: git_url, branch }
                    } else if let Some(path) = get_string(spec_table, "path") {
                        DependencySource::Local(PathBuf::from(path))
                    } else if let Some(registry) = get_string(spec_table, "registry") {
                        DependencySource::Registry(registry)
                    } else {
                        DependencySource::Builtin
                    };
                    
                    DependencySpec {
                        name: name.clone(),
                        version,
                        source,
                        features,
                    }
                }
                _ => continue,
            };
            
            map.insert(name.clone(), spec);
        }
    }
    
    map
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_simple_manifest() {
        let toml_str = r#"
[package]
name = "test-app"
version = "1.0.0"

[dependencies]
omni-std = "1.0.0"
omni-net = "1.0.0"

[dev-dependencies]
omni-test = "1.0.0"

[scripts]
dev = "omni serve"
build = "omni build --release"

[permissions]
allow_thread = true
"#;
        let manifest = OmniManifest::parse(toml_str).unwrap();
        assert_eq!(manifest.package.name, "test-app");
        assert_eq!(manifest.package.version, "1.0.0");
        assert_eq!(manifest.dependencies.len(), 2);
        assert_eq!(manifest.dev_dependencies.len(), 1);
        assert!(manifest.has_dependency("omni-std"));
        assert!(manifest.has_dependency("omni-test"));
        assert!(!manifest.has_dependency("nonexistent"));
        assert_eq!(manifest.scripts.get("dev").unwrap(), "omni serve");
        assert!(manifest.permissions.allow_thread);
    }

    #[test]
    fn test_parse_complex_dependency() {
        let toml_str = r#"
[package]
name = "complex-app"

[dependencies]
omni-std = "1.0.0"
my-lib = { version = "2.0.0", git = "https://github.com/user/lib.git", branch = "main" }
local-pkg = { version = "0.1.0", path = "../my-local-pkg" }
"#;
        let manifest = OmniManifest::parse(toml_str).unwrap();
        assert_eq!(manifest.dependencies.len(), 3);
        
        let my_lib = manifest.dependencies.get("my-lib").unwrap();
        assert!(matches!(my_lib.source, DependencySource::Git { .. }));
        
        let local = manifest.dependencies.get("local-pkg").unwrap();
        assert!(matches!(local.source, DependencySource::Local(_)));
    }
}
