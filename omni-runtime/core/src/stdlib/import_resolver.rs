// ==========================================
// 🔗 OMNI IMPORT RESOLVER — Phase 15
// ==========================================
// Resolves `import "std:*"` directives from .omni source files
// into executable JavaScript bootstrap code.
//
// ALUR:
//   1. Parse source code untuk menemukan semua `import "..."` 
//   2. Klasifikasikan: std:* (native), omni_modules/* (package), atau relative
//   3. Resolve setiap import menjadi JavaScript bootstrap yang siap injeksi
//   4. Kembalikan daftar resolved imports ke caller (engine/V8)
//
// TIPE IMPORT:
//   import "std:crypto"       → Native stdlib JS module
//   import "std:net"          → Native stdlib JS module
//   import "std:math"         → Native stdlib JS module
//   import "omni-auth"        → Package dari omni_modules/
//   import "./utils"          → Relative file import
// ==========================================

/// Tipe import yang dikenali oleh resolver
#[derive(Debug, Clone, PartialEq)]
pub enum ImportKind {
    /// Native standard library: `import "std:crypto"`, `import "std:net"`
    StdLib(String),
    /// Package dari omni_modules: `import "omni-auth"`, `import "omni-db"`
    Package(String),
    /// Relative file: `import "./utils"`, `import "../shared/types"`
    Relative(String),
    /// Unknown/invalid import
    Unknown(String),
}

/// Satu import directive yang sudah di-resolve
#[derive(Debug, Clone)]
pub struct ResolvedImport {
    /// Raw import path dari source code
    pub raw_path: String,
    /// Tipe import (std, package, relative)
    pub kind: ImportKind,
    /// JavaScript code yang harus diinjeksi ke V8
    pub js_bootstrap: String,
    /// Apakah berhasil di-resolve
    pub resolved: bool,
}

/// Hasil resolusi seluruh imports dari satu file
#[derive(Debug)]
pub struct ImportResolution {
    /// Semua imports yang ditemukan dan di-resolve
    pub imports: Vec<ResolvedImport>,
    /// JavaScript bootstrap gabungan (siap injeksi ke V8)
    pub combined_bootstrap: String,
    /// Jumlah import yang gagal di-resolve
    pub failed_count: usize,
}

// ==========================================
// 📦 STDLIB MODULE REGISTRY
// ==========================================

/// Map nama modul std:* ke file JS yang di-embed
/// Setiap modul ini sudah ada di src/stdlib/js/*.js
/// dan di-include via `include_str!` di runtime.rs
const JS_RUNTIME: &str = include_str!("js/runtime.js");
const JS_MATH: &str = include_str!("js/math.js");
const JS_COLLECTIONS: &str = include_str!("js/collections.js");
const JS_GRAPH: &str = include_str!("js/graph.js");
const JS_UI: &str = include_str!("js/ui.js");
const JS_TIME: &str = include_str!("js/time.js");
const JS_CRYPTO: &str = include_str!("js/crypto.js");
const JS_NET: &str = include_str!("js/net.js");
const JS_STRING: &str = include_str!("js/string.js");

/// Resolve nama modul std:* ke JavaScript bootstrap code
pub fn resolve_stdlib_module(module_name: &str) -> Option<&'static str> {
    match module_name {
        "runtime" | "core"       => Some(JS_RUNTIME),
        "math" | "tensor"        => Some(JS_MATH),
        "collections" | "array"  => Some(JS_COLLECTIONS),
        "graph" | "graphql"      => Some(JS_GRAPH),
        "ui" | "dom"             => Some(JS_UI),
        "time" | "timer"         => Some(JS_TIME),
        "crypto" | "hash"        => Some(JS_CRYPTO),
        "net" | "http" | "fetch" => Some(JS_NET),
        "string" | "str"         => Some(JS_STRING),
        "net/http"               => Some(JS_NET),
        "net/ws"                 => Some(JS_NET),
        "db/postgres"            => None, // Future: database module
        "db/redis"               => None, // Future: redis module
        "ai/tensor"              => Some(JS_MATH), // Alias ke math (tensor ops)
        "fs/zero_copy"           => None, // Handled by native syscalls
        "sys"                    => None, // Handled by native syscalls
        _                        => None,
    }
}

// ==========================================
// 🔍 IMPORT PARSER
// ==========================================

/// Parse source code `.omni` untuk menemukan semua `import "..."` directives.
/// Mendukung format:
///   - `import "std:crypto"`
///   - `import "std:net/http"`
///   - `import "omni-auth"`
///   - `import "./utils"`
pub fn parse_imports(source: &str) -> Vec<String> {
    let mut imports = Vec::new();
    
    for line in source.lines() {
        let trimmed = line.trim();
        
        // Skip komentar
        if trimmed.starts_with("//") || trimmed.starts_with("/*") {
            continue;
        }
        
        // Format: import "path" atau import 'path'
        if trimmed.starts_with("import ") {
            // Extract path dari import statement
            if let Some(path) = extract_import_path(trimmed) {
                imports.push(path);
            }
        }
        
        // Juga support format: gunakan "path" (Bahasa Indonesia syntax)
        if trimmed.starts_with("gunakan ") {
            if let Some(path) = extract_import_path(trimmed) {
                imports.push(path);
            }
        }
    }
    
    imports
}

/// Extract path dari import statement
/// Contoh: `import "std:crypto"` → `std:crypto`
fn extract_import_path(line: &str) -> Option<String> {
    // Cari bagian yang diapit tanda kutip
    let start_double = line.find('"');
    let start_single = line.find('\'');
    
    let (start_char, end_char) = match (start_double, start_single) {
        (Some(d), Some(s)) => {
            if d < s { (d, '"') } else { (s, '\'') }
        }
        (Some(d), None) => (d, '"'),
        (None, Some(s)) => (s, '\''),
        (None, None) => return None,
    };
    
    let rest = &line[start_char + 1..];
    if let Some(end_pos) = rest.find(end_char) {
        Some(rest[..end_pos].to_string())
    } else {
        None
    }
}

/// Klasifikasikan raw import path ke ImportKind
fn classify_import(path: &str) -> ImportKind {
    if path.starts_with("std:") {
        // Strip prefix "std:" dan ambil module name
        let module = path.strip_prefix("std:").unwrap_or(path);
        ImportKind::StdLib(module.to_string())
    } else if path.starts_with("./") || path.starts_with("../") {
        ImportKind::Relative(path.to_string())
    } else if path.starts_with("omni-") || path.starts_with('@') {
        ImportKind::Package(path.to_string())
    } else {
        // Default: coba sebagai package
        ImportKind::Package(path.to_string())
    }
}

// ==========================================
// ⚡ RESOLVER ENGINE
// ==========================================

/// Resolve semua import directives dari source code `.omni`.
/// Mengembalikan ImportResolution berisi JavaScript bootstrap
/// yang siap diinjeksi ke V8 sebelum user code.
pub fn resolve_imports(source: &str, project_dir: Option<&std::path::Path>) -> ImportResolution {
    let raw_imports = parse_imports(source);
    let mut resolved_imports = Vec::new();
    let mut bootstrap_parts = Vec::new();
    let mut failed_count = 0;
    
    // Runtime SELALU di-load pertama (mendefinisikan __omni_output, print, dll)
    bootstrap_parts.push("// ═══ OMNI-STD BOOTSTRAP (Phase 15) ═══".to_string());
    bootstrap_parts.push(JS_RUNTIME.to_string());
    bootstrap_parts.push(JS_TIME.to_string()); // setTimeout polyfill selalu ada

    for raw_path in &raw_imports {
        let kind = classify_import(raw_path);
        
        let (js_code, success) = match &kind {
            ImportKind::StdLib(module) => {
                match resolve_stdlib_module(module) {
                    Some(js) => {
                        println!("📦 [IMPORT] Resolved std:{} → {} bytes JS", module, js.len());
                        (js.to_string(), true)
                    }
                    None => {
                        // Module tidak punya JS counterpart → akan dihandle via syscall
                        eprintln!("⚠️ [IMPORT] std:{} → Tidak ada JS bootstrap (native-only syscall)", module);
                        (format!(
                            "// std:{module} — Native-only module (gunakan OmniNative.syscall)\n\
                             globalThis.__omni_modules = globalThis.__omni_modules || {{}};\n\
                             globalThis.__omni_modules[\"{module}\"] = {{ native: true, loaded: true }};\n",
                            module = module
                        ), true)
                    }
                }
            }
            ImportKind::Package(pkg_name) => {
                // Coba baca dari omni_modules/<pkg>/src/lib.omni
                match resolve_package_import(pkg_name, project_dir) {
                    Some(js) => (js, true),
                    None => {
                        failed_count += 1;
                        (format!("// ❌ Package '{}' tidak ditemukan di omni_modules/\n", pkg_name), false)
                    }
                }
            }
            ImportKind::Relative(rel_path) => {
                match resolve_relative_import(rel_path, project_dir) {
                    Some(js) => (js, true),
                    None => {
                        failed_count += 1;
                        (format!("// ❌ File '{}' tidak ditemukan\n", rel_path), false)
                    }
                }
            }
            ImportKind::Unknown(path) => {
                failed_count += 1;
                (format!("// ❌ Unknown import: '{}'\n", path), false)
            }
        };

        bootstrap_parts.push(js_code.clone());

        resolved_imports.push(ResolvedImport {
            raw_path: raw_path.clone(),
            kind,
            js_bootstrap: js_code,
            resolved: success,
        });
    }
    
    bootstrap_parts.push("// ═══ END OMNI IMPORTS ═══".to_string());

    ImportResolution {
        imports: resolved_imports,
        combined_bootstrap: bootstrap_parts.join("\n\n"),
        failed_count,
    }
}

/// Resolve package import dari omni_modules/
fn resolve_package_import(pkg_name: &str, project_dir: Option<&std::path::Path>) -> Option<String> {
    let base = project_dir.unwrap_or_else(|| std::path::Path::new("."));
    
    // Coba beberapa lokasi:
    // 1. omni_modules/<pkg>/src/lib.omni
    // 2. omni_modules/<pkg>/src/index.js
    // 3. omni_modules/<pkg>/lib.omni
    let candidates = [
        base.join("omni_modules").join(pkg_name).join("src").join("lib.omni"),
        base.join("omni_modules").join(pkg_name).join("src").join("index.js"),
        base.join("omni_modules").join(pkg_name).join("lib.omni"),
    ];
    
    for path in &candidates {
        if path.exists() {
            if let Ok(content) = std::fs::read_to_string(path) {
                println!("📦 [IMPORT] Package {} resolved → {}", pkg_name, path.display());
                return Some(format!(
                    "// ═══ Package: {} ═══\n{}\n",
                    pkg_name, content
                ));
            }
        }
    }
    
    eprintln!("⚠️ [IMPORT] Package '{}' tidak ditemukan di omni_modules/", pkg_name);
    None
}

/// Resolve relative import dari file path
fn resolve_relative_import(rel_path: &str, project_dir: Option<&std::path::Path>) -> Option<String> {
    let base = project_dir.unwrap_or_else(|| std::path::Path::new("."));
    
    // Tambahkan ekstensi .omni jika belum ada
    let candidates = if rel_path.contains('.') {
        vec![base.join(rel_path)]
    } else {
        vec![
            base.join(format!("{}.omni", rel_path)),
            base.join(format!("{}.js", rel_path)),
            base.join(rel_path).join("index.omni"),
        ]
    };
    
    for path in &candidates {
        if path.exists() {
            if let Ok(content) = std::fs::read_to_string(path) {
                println!("📦 [IMPORT] Relative {} resolved → {}", rel_path, path.display());
                return Some(format!(
                    "// ═══ Import: {} ═══\n{}\n",
                    rel_path, content
                ));
            }
        }
    }
    
    None
}

/// Resolve selective modules — hanya modul yang di-import (bukan semua sekaligus)
/// Ini adalah pengganti `get_full_runtime()` yang lebih efisien.
pub fn get_selective_runtime(imports: &[ResolvedImport]) -> String {
    let mut parts = Vec::new();
    parts.push("// ═══ OMNI-STD v2.0.0 (Selective) ═══".to_string());
    
    // Runtime core SELALU di-load
    parts.push(JS_RUNTIME.to_string());
    parts.push(JS_TIME.to_string());
    
    // Hanya load modul yang di-import
    let mut loaded: std::collections::HashSet<String> = std::collections::HashSet::new();
    loaded.insert("runtime".to_string());
    loaded.insert("time".to_string());
    
    for import in imports {
        if let ImportKind::StdLib(module) = &import.kind {
            if loaded.contains(module.as_str()) {
                continue;
            }
            if let Some(js) = resolve_stdlib_module(module) {
                parts.push(format!("// ═══ std:{} ═══", module));
                parts.push(js.to_string());
                loaded.insert(module.clone());
            }
        }
    }
    
    parts.push("// ═══ END OMNI-STD ═══".to_string());
    parts.join("\n\n")
}

// ==========================================
// 🧪 TESTS
// ==========================================

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_imports_basic() {
        let source = r#"
import "std:crypto"
import "std:net"
import "std:math"

fn main() {
    let hash = OmniCrypto.sha256("hello")
}
"#;
        let imports = parse_imports(source);
        assert_eq!(imports.len(), 3);
        assert_eq!(imports[0], "std:crypto");
        assert_eq!(imports[1], "std:net");
        assert_eq!(imports[2], "std:math");
    }

    #[test]
    fn test_parse_imports_single_quotes() {
        let source = "import 'std:string'\nimport 'std:time'\n";
        let imports = parse_imports(source);
        assert_eq!(imports.len(), 2);
        assert_eq!(imports[0], "std:string");
    }

    #[test]
    fn test_parse_imports_gunakan() {
        let source = "gunakan \"std:crypto\"\ngunakan \"std:net\"\n";
        let imports = parse_imports(source);
        assert_eq!(imports.len(), 2);
    }

    #[test]
    fn test_classify_import() {
        assert_eq!(classify_import("std:crypto"), ImportKind::StdLib("crypto".to_string()));
        assert_eq!(classify_import("./utils"), ImportKind::Relative("./utils".to_string()));
        assert_eq!(classify_import("omni-auth"), ImportKind::Package("omni-auth".to_string()));
    }

    #[test]
    fn test_resolve_stdlib_crypto() {
        let js = resolve_stdlib_module("crypto");
        assert!(js.is_some());
        assert!(js.unwrap().contains("OmniCrypto"));
    }

    #[test]
    fn test_resolve_stdlib_net() {
        let js = resolve_stdlib_module("net");
        assert!(js.is_some());
    }

    #[test]
    fn test_resolve_unknown_module() {
        let js = resolve_stdlib_module("nonexistent_module_xyz");
        assert!(js.is_none());
    }

    #[test]
    fn test_full_resolve() {
        let source = r#"
import "std:crypto"
import "std:math"
"#;
        let resolution = resolve_imports(source, None);
        assert_eq!(resolution.imports.len(), 2);
        assert!(resolution.imports[0].resolved);
        assert!(resolution.imports[1].resolved);
        assert_eq!(resolution.failed_count, 0);
        assert!(resolution.combined_bootstrap.contains("OmniCrypto"));
    }

    #[test]
    fn test_skip_comments() {
        let source = r#"
// import "std:crypto"
/* import "std:net" */
import "std:math"
"#;
        let imports = parse_imports(source);
        assert_eq!(imports.len(), 1);
        assert_eq!(imports[0], "std:math");
    }
}
