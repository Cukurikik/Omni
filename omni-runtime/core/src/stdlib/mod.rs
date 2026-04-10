pub mod net;
pub mod crypto;
pub mod concurrency;
pub mod tensor;
pub mod db;
pub mod runtime;
pub mod import_resolver;

/// The Native Arsenal Registry 
/// Modules inside `std:*` are bound directly into the FFI interpreter memory.
/// They do not require package resolution or downloading.
pub struct NativeArsenal;

impl NativeArsenal {
    pub fn is_native_module(name: &str) -> bool {
        name.starts_with("std:")
    }

    pub fn resolve(name: &str) -> Option<&'static str> {
        match name {
            "std:net/http" => Some("0xNATIVE_NET_HTTP"),
            "std:net/ws" => Some("0xNATIVE_NET_WS"),
            "std:crypto" => Some("0xNATIVE_CRYPTO"),
            "std:concurrency" => Some("0xNATIVE_CONCURRENCY"),
            "std:db/postgres" => Some("0xNATIVE_DB_POSTGRES"),
            "std:db/redis" => Some("0xNATIVE_DB_REDIS"),
            "std:graphql" => Some("0xNATIVE_GRAPHQL"),
            "std:ai/tensor" => Some("0xNATIVE_AI_TENSOR"),
            "std:fs/zero_copy" => Some("0xNATIVE_FS_ZERO_COPY"),
            "std:sys" => Some("0xNATIVE_SYS"),
            "std:math" => Some("0xNATIVE_MATH"),
            "std:string" => Some("0xNATIVE_STRING"),
            "std:time" => Some("0xNATIVE_TIME"),
            "std:collections" => Some("0xNATIVE_COLLECTIONS"),
            "std:ui" => Some("0xNATIVE_UI"),
            "std:net" => Some("0xNATIVE_NET"),
            _ => None,
        }
    }

    /// Mendapatkan JavaScript bootstrap code untuk modul std:*
    /// Menggunakan ImportResolver untuk resolve ke file JS yang benar
    pub fn get_js_bootstrap(module_path: &str) -> Option<String> {
        if !Self::is_native_module(module_path) {
            return None;
        }

        let module_name = module_path.strip_prefix("std:").unwrap_or(module_path);
        import_resolver::resolve_stdlib_module(module_name)
            .map(|js| js.to_string())
    }

    /// Daftar semua modul native yang tersedia
    pub fn list_available() -> Vec<&'static str> {
        vec![
            "std:crypto", "std:net", "std:net/http", "std:net/ws",
            "std:math", "std:string", "std:time", "std:collections",
            "std:graphql", "std:ui", "std:concurrency",
            "std:db/postgres", "std:db/redis",
            "std:ai/tensor", "std:fs/zero_copy", "std:sys",
        ]
    }
}
