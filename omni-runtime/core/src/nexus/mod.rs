// ==========================================
// 📦 OMNI NEXUS: Decentralized Package Registry
// ==========================================
// Bahasa pemrograman modern mati jika registry-nya mati.
// OMNI Nexus tidak mengandalkan server pusat.
// Setiap paket divalidasi oleh Blockchain Hash di dalam Omnifile.
// ==========================================

pub mod registry;
pub mod resolver;
pub mod nexus_manifest;
pub mod vault;
pub mod lock;
pub mod sandbox;
pub mod hijacker;
pub mod workspace;


use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};

/// Representasi satu dependency di dalam Omnifile [dependencies]
#[derive(Debug, Clone)]
pub struct OmniDependency {
    pub name: String,
    pub version: String,
    pub hash: String, // SHA-256 blockchain hash
    pub resolved: bool,
}

/// Omnifile manifest parser
#[derive(Debug)]
pub struct OmniManifest {
    pub project_name: String,
    pub version: String,
    pub compiler_version: String,
    pub dependencies: Vec<OmniDependency>,
    pub permissions: ManifestPermissions,
    pub workspace_members: Vec<String>,
}

#[derive(Debug, Default)]
pub struct ManifestPermissions {
    pub allow_network: Vec<String>,
    pub allow_file_system: Vec<String>,
}

impl OmniManifest {
    /// Parse Omnifile dari path yang diberikan
    pub fn parse(path: &Path) -> Result<Self, String> {
        let content = fs::read_to_string(path)
            .map_err(|e| format!("❌ Nexus: Gagal membaca Omnifile: {}", e))?;

        Self::parse_content(&content)
    }

    /// Parse isi Omnifile string
    pub fn parse_content(content: &str) -> Result<Self, String> {
        let mut manifest = OmniManifest {
            project_name: String::new(),
            version: String::new(),
            compiler_version: String::new(),
            dependencies: Vec::new(),
            permissions: ManifestPermissions::default(),
            workspace_members: Vec::new(),
        };

        let mut current_section = "";

        for line in content.lines() {
            let trimmed = line.trim();

            // Skip empty lines and comments
            if trimmed.is_empty() || trimmed.starts_with('#') {
                continue;
            }

            // Section headers
            if trimmed.starts_with('[') && trimmed.ends_with(']') {
                current_section = match trimmed {
                    "[project]" => "project",
                    "[dependencies]" => "dependencies",
                    "[permissions]" => "permissions",
                    _ => "unknown",
                };
                continue;
            }

            // Key-value pairs
            if let Some((key, value)) = trimmed.split_once('=') {
                let key = key.trim();
                let value = value.trim().trim_matches('"');

                match current_section {
                    "project" => match key {
                        "name" => manifest.project_name = value.to_string(),
                        "version" => manifest.version = value.to_string(),
                        "compiler_version" => manifest.compiler_version = value.to_string(),
                        _ => {}
                    },
                    "dependencies" => {
                        // Parse: package_name = { version = "x.y.z", hash = "sha256:..." }
                        let dep = Self::parse_dependency(key, value)?;
                        manifest.dependencies.push(dep);
                    }
                    "permissions" => match key {
                        "allow_network" => {
                            manifest.permissions.allow_network = Self::parse_array(value);
                        }
                        "allow_file_system" => {
                            manifest.permissions.allow_file_system = Self::parse_array(value);
                        }
                        _ => {}
                    },
                    "workspace" => match key {
                        "members" => {
                            manifest.workspace_members = Self::parse_array(value);
                        }
                        _ => {}
                    },
                    _ => {}
                }
            }
        }

        Ok(manifest)
    }

    fn parse_dependency(name: &str, value: &str) -> Result<OmniDependency, String> {
        // Simple parser for: { version = "2.1.0", hash = "sha256:8f3a...b2c1" }
        let cleaned = value.trim_matches(|c| c == '{' || c == '}').trim();
        let mut version = String::new();
        let mut hash = String::new();

        for part in cleaned.split(',') {
            if let Some((k, v)) = part.split_once('=') {
                let k = k.trim();
                let v = v.trim().trim_matches('"').trim();
                match k {
                    "version" => version = v.to_string(),
                    "hash" => hash = v.to_string(),
                    _ => {}
                }
            }
        }

        Ok(OmniDependency {
            name: name.to_string(),
            version,
            hash,
            resolved: false,
        })
    }

    fn parse_array(value: &str) -> Vec<String> {
        value
            .trim_matches(|c| c == '[' || c == ']')
            .split(',')
            .map(|s| s.trim().trim_matches('"').to_string())
            .filter(|s| !s.is_empty())
            .collect()
    }
}

/// Menghasilkan Omnifile.lock untuk reproducible builds
pub fn generate_lockfile(
    manifest: &OmniManifest,
    resolved: &HashMap<String, ResolvedPackage>,
) -> String {
    let mut lock = String::new();
    lock.push_str("# Omnifile.lock — AUTO-GENERATED BY OMNI NEXUS\n");
    lock.push_str(&format!(
        "# Project: {} v{}\n",
        manifest.project_name, manifest.version
    ));
    lock.push_str(&format!("# Generated: {}\n\n", chrono_stub()));

    for dep in &manifest.dependencies {
        if let Some(pkg) = resolved.get(&dep.name) {
            lock.push_str(&format!("[[package]]\n"));
            lock.push_str(&format!("name = \"{}\"\n", pkg.name));
            lock.push_str(&format!("version = \"{}\"\n", pkg.version));
            lock.push_str(&format!("hash = \"{}\"\n", pkg.hash));
            lock.push_str(&format!("source = \"{}\"\n", pkg.source));
            lock.push_str(&format!(
                "integrity = \"{}\"\n\n",
                if pkg.verified {
                    "VERIFIED"
                } else {
                    "UNVERIFIED"
                }
            ));
        }
    }

    lock
}

/// Stub untuk timestamp (tidak mau tambah chrono dependency)
fn chrono_stub() -> String {
    "2026-04-05T00:00:00Z".to_string()
}

/// Resolved package info
#[derive(Debug, Clone)]
pub struct ResolvedPackage {
    pub name: String,
    pub version: String,
    pub hash: String,
    pub source: String, // "nexus://p2p" atau "local://cache"
    pub verified: bool,
    pub cache_path: PathBuf,
}
