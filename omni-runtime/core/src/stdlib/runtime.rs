// ═══════════════════════════════════════════════════════════
// OMNI-STD RUNTIME LOADER
// ═══════════════════════════════════════════════════════════
// Memuat semua modul JavaScript standard library dan
// menggabungkannya menjadi satu bootstrap string untuk
// diinjeksi ke V8 Isolate sebelum user code dieksekusi.
// ═══════════════════════════════════════════════════════════

/// Core runtime: print, console, assert, type helpers
const JS_RUNTIME: &str = include_str!("js/runtime.js");

/// OmniMath: tensor ops, linear algebra, statistics, ML activations
const JS_MATH: &str = include_str!("js/math.js");

/// OmniCollections: array/map/set helpers
const JS_COLLECTIONS: &str = include_str!("js/collections.js");

/// OmniGraph: GraphQL query runtime
const JS_GRAPH: &str = include_str!("js/graph.js");

/// OmniUI: virtual DOM, component system, SSR
const JS_UI: &str = include_str!("js/ui.js");

/// OmniTime: setTimeout polyfill, timing, benchmarks
const JS_TIME: &str = include_str!("js/time.js");

/// OmniCrypto: UUID, hashing, base64, random
const JS_CRYPTO: &str = include_str!("js/crypto.js");

/// OmniNet: fetch polyfill, HTTP helpers, URL builder
const JS_NET: &str = include_str!("js/net.js");

/// OmniString: string manipulation utilities
const JS_STRING: &str = include_str!("js/string.js");

/// Mengembalikan seluruh OMNI Standard Library sebagai satu string JavaScript.
/// Urutan penting: runtime HARUS pertama (mendefinisikan __omni_output).
pub fn get_full_runtime() -> String {
    [
        "// ═══ OMNI-STD v2.0.0 ═══",
        JS_RUNTIME,     // PERTAMA: print(), console, __omni_output
        JS_TIME,        // setTimeout, OmniTime (perlu sebelum user code)
        JS_MATH,        // OmniMath
        JS_COLLECTIONS, // OmniCollections
        JS_GRAPH,       // OmniGraph
        JS_UI,          // OmniUI
        JS_CRYPTO,      // OmniCrypto
        JS_NET,         // OmniNet, fetch polyfill
        JS_STRING,      // OmniString
        "// ═══ END OMNI-STD ═══",
    ].join("\n\n")
}

/// Mengembalikan info versi runtime
pub fn runtime_info() -> &'static str {
    "omni-std v2.0.0 | Modules: Runtime, Math, Collections, Graph, UI, Time, Crypto, Net, String"
}

/// Mengembalikan JavaScript code untuk satu modul berdasarkan nama.
/// Digunakan oleh ImportResolver untuk selective loading (Phase 15).
pub fn get_module_runtime(module_name: &str) -> Option<&'static str> {
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
        _                        => None,
    }
}

/// Mengembalikan daftar semua modul yang tersedia
pub fn list_modules() -> Vec<&'static str> {
    vec![
        "OmniMath        — Tensor ops, linear algebra, statistics, ML activations",
        "OmniCollections — Array/Map/Set utilities (chunk, flatten, zip, group_by)",
        "OmniGraph       — GraphQL query builder & executor",
        "OmniUI          — Virtual DOM, component system, SSR rendering",
        "OmniTime        — Timing, benchmarks, date formatting",
        "OmniCrypto      — UUID, hashing, base64, random generators",
        "OmniNet         — Fetch, HTTP helpers, URL builder",
        "OmniString      — String manipulation (camelCase, slugify, template)",
    ]
}
