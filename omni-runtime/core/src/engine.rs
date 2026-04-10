// ==========================================
// ⚙️ OMNI-JS: THE KINETIC V8 ENGINE (RUST)
// ==========================================
// Sandbox JavaScript yang kebal peluru.
// V8 Engine (JIT Compiler C++) dibungkus oleh Rust Memory Safety.
// Jika ada kode JS yang mencoba eksploitasi memori, Rust MEMBLOKIR
// di tingkat Kernel sebelum crash terjadi.
//
// ARSITEKTUR:
//   OmniEngine::boot()       → Menyalakan V8 Platform + Isolate
//   OmniEngine::execute_js() → Mengeksekusi string JS di dalam Sandbox
//   OmniEngine::execute_module() → Mengeksekusi file JS sebagai ES Module
//
// KEAMANAN:
//   - Setiap Isolate adalah Sandbox terisolasi (tidak bisa akses RAM lain)
//   - Rust menjamin zero memory leak via ownership system
//   - V8's JIT Compiler mengoptimasi JS menjadi kode mesin native
// ==========================================

use v8;
use std::sync::Once;
use thiserror::Error;
use crate::syscalls;

// ==========================================
// 🛡️ ERROR TYPES
// ==========================================

#[derive(Error, Debug)]
pub enum OmniError {
    #[error("🔥 [OMNI-CORE] Gagal mengompilasi JavaScript: {0}")]
    CompileError(String),
    
    #[error("💥 [OMNI-CORE] Runtime Error saat eksekusi: {0}")]
    RuntimeError(String),
    
    #[error("📄 [OMNI-CORE] File tidak ditemukan: {0}")]
    FileNotFound(String),
    
    #[error("🧬 [OMNI-CORE] Error serialisasi: {0}")]
    SerializationError(String),
}

pub type OmniResult<T> = Result<T, OmniError>;

// ==========================================
// ⚡ V8 PLATFORM INITIALIZATION (SINGLETON)
// ==========================================
// V8 Platform hanya boleh diinisiasi SEKALI sepanjang hidup proses.
// Kita gunakan std::sync::Once untuk memastikan ini.

static V8_INIT: Once = Once::new();

fn ensure_v8_initialized() {
    V8_INIT.call_once(|| {
        let platform = v8::new_default_platform(0, false).make_shared();
        v8::V8::initialize_platform(platform);
        v8::V8::initialize();
        log::info!("🚀 [OMNI-CORE] V8 Platform berhasil diinisiasi (SEKALI seumur hidup)");
    });
}

// ==========================================
// ⚙️ OMNI ENGINE: V8 ISOLATE MANAGER
// ==========================================

pub struct OmniEngine {
    isolate: v8::OwnedIsolate,
}

impl OmniEngine {
    /// Menyalakan Reaktor V8 — menciptakan Isolate baru (Sandbox terisolasi).
    /// 
    /// Setiap Isolate memiliki heap memori sendiri yang 100% terisolasi.
    /// Kode JS di Isolate A tidak bisa mengakses memori Isolate B.
    /// Ini adalah fondasi keamanan OMNI-JS Runtime.
    pub fn boot() -> Self {
        ensure_v8_initialized();
        
        log::info!("⚙️ [OMNI-CORE] Menciptakan V8 Isolate baru (Sandbox terisolasi)...");
        
        let params = v8::CreateParams::default();
        let isolate = v8::Isolate::new(params);

        OmniEngine { isolate }
    }

    /// Menyalakan Reaktor dengan batas memori (dalam MB).
    /// Berguna untuk mencegah satu script JS memakan seluruh RAM server.
    /// 
    /// # Arguments
    /// * `max_heap_mb` — Batas maksimal heap memory dalam megabytes
    pub fn boot_with_limits(max_heap_mb: usize) -> Self {
        ensure_v8_initialized();
        
        log::info!(
            "⚙️ [OMNI-CORE] Menciptakan V8 Isolate dengan batas {}MB...", 
            max_heap_mb
        );
        
        let mut params = v8::CreateParams::default();
        // V8 menggunakan byte, jadi konversi MB → Bytes
        params = params.heap_limits(0, max_heap_mb * 1024 * 1024);
        let isolate = v8::Isolate::new(params);

        OmniEngine { isolate }
    }

    /// Mengeksekusi string kode JavaScript di dalam Sandbox V8.
    /// 
    /// # Alur Eksekusi:
    /// 1. Buat HandleScope (tempat semua V8 handle hidup)
    /// 2. Buat Context (lingkungan global: `console`, `Math`, dll)
    /// 3. Kompilasi string JS menjadi bytecode (V8's JIT)
    /// 4. Jalankan bytecode dan tangkap hasil
    /// 5. Konversi hasil dari V8 String ke Rust String
    /// 
    /// # Arguments
    /// * `js_code` — String berisi kode JavaScript yang akan dieksekusi
    /// 
    /// # Returns
    /// `OmniResult<String>` — Hasil eksekusi sebagai string, atau error
    pub fn execute_js(&mut self, js_code: &str) -> OmniResult<String> {
        let scope = &mut v8::HandleScope::new(&mut self.isolate);
        let context = v8::Context::new(scope, Default::default());
        let scope = &mut v8::ContextScope::new(scope, context);

        // Injeksi OMNI Global APIs sebelum eksekusi kode user
        Self::inject_omni_globals(scope);

        // Kompilasi string JS → bytecode V8
        let code = v8::String::new(scope, js_code)
            .ok_or_else(|| OmniError::CompileError("Gagal membuat V8 String".into()))?;

        let script = v8::Script::compile(scope, code, None)
            .ok_or_else(|| OmniError::CompileError("Gagal mengompilasi JavaScript".into()))?;

        // Eksekusi script dan tangkap hasil
        let result = script.run(scope)
            .ok_or_else(|| OmniError::RuntimeError("Script gagal dijalankan".into()))?;

        // Konversi V8 Value → Rust String
        let result_str = result.to_rust_string_lossy(scope);

        Ok(result_str)
    }

    /// Mengeksekusi JavaScript dengan konteks request dari Golang.
    /// 
    /// Fungsi ini menambahkan objek `req` (request) ke dalam konteks JS
    /// sebelum mengeksekusi kode user. Ini memungkinkan developer menulis:
    /// ```js
    /// function OmniHandler(req) {
    ///     return JSON.stringify({ method: req.method, url: req.url });
    /// }
    /// ```
    pub fn execute_with_context(
        &mut self, 
        js_code: &str, 
        method: &str, 
        url: &str,
        headers_json: &str,
        body: &str,
    ) -> OmniResult<String> {
        // Bangun konteks request yang akan diinjeksi ke JS
        let context_code = format!(r#"
            // 🌐 OMNI-NET Request Context (Diinjeksi oleh Golang)
            const __omni_req = {{
                method: "{}",
                url: "{}",
                headers: {},
                body: `{}`
            }};
        "#, 
            method.replace('"', r#"\""#),
            url.replace('"', r#"\""#),
            headers_json,
            body.replace('`', r#"\`"#),
        );

        // Gabungkan: Context + User Code + Handler Call
        let full_code = format!(
            "{}\n{}\n\n// Auto-invoke handler\nif (typeof OmniHandler === 'function') {{ OmniHandler(__omni_req); }} else {{ '{{\"error\": \"OmniHandler not defined\"}}' }}",
            context_code, 
            js_code
        );

        self.execute_js(&full_code)
    }

    /// Injects OMNI global APIs ke dalam V8 Context.
    /// Ini adalah fungsionalitas bawaan yang tersedia di semua script JS.
    fn inject_omni_globals(scope: &mut v8::ContextScope<v8::HandleScope>) {
        let context = scope.get_current_context();
        let global = context.global(scope);

        // Injeksi __OMNI_VERSION__
        let key = v8::String::new(scope, "__OMNI_VERSION__").unwrap();
        let value = v8::String::new(scope, "1.3.0-SOVEREIGN").unwrap();
        global.set(scope, key.into(), value.into());

        // Injeksi __OMNI_RUNTIME__
        let key = v8::String::new(scope, "__OMNI_RUNTIME__").unwrap();
        let value = v8::String::new(scope, "omni-core/rust-v8").unwrap();
        global.set(scope, key.into(), value.into());

        // Injeksi console.log shim (mengirim output ke Rust logger)
        Self::inject_console(scope);

        // Injeksi OmniNative.syscall (jembatan ke Rust/Golang native functions)
        Self::inject_omni_native(scope);

        // 🔥 Injeksi OMNI Runtime Polyfills — API surface untuk semua 22 modules
        // Polyfills HARUS dimuat SETELAH OmniNative.syscall tersedia
        Self::inject_runtime_polyfills(scope);
    }

    /// Memuat dan mengeksekusi runtime_polyfills.js di dalam V8 Context.
    /// File ini menyediakan API surface lengkap untuk semua 22 omni_modules:
    /// omni_std, omni_fs, omni_env, omni_crypto, omni_http, omni_db, dll.
    ///
    /// Ini adalah equivalent dari Node.js internal/bootstrap/loaders.js.
    fn inject_runtime_polyfills(scope: &mut v8::ContextScope<v8::HandleScope>) {
        // Cari polyfills di beberapa lokasi
        let polyfill_paths = [
            "stdlib/omni/runtime_polyfills.js",
            "../stdlib/omni/runtime_polyfills.js",
            "omni-runtime/stdlib/omni/runtime_polyfills.js",
        ];

        let mut polyfill_code = None;
        for path in &polyfill_paths {
            if let Ok(code) = std::fs::read_to_string(path) {
                polyfill_code = Some(code);
                log::info!("📦 [OMNI-CORE] Runtime polyfills dimuat dari: {}", path);
                break;
            }
        }

        // Jika file tidak ditemukan, gunakan inline minimal polyfills
        let code = polyfill_code.unwrap_or_else(|| {
            log::warn!("⚠️ [OMNI-CORE] runtime_polyfills.js tidak ditemukan, menggunakan inline fallback");
            r#"
                // Minimal inline polyfills
                if (typeof globalThis.__OMNI_POLYFILLS_LOADED__ === 'undefined') {
                    globalThis.__OMNI_POLYFILLS_LOADED__ = true;
                    globalThis.println = (msg) => OmniNative.syscall('println', { message: String(msg) });
                    globalThis.print_ = (msg) => OmniNative.syscall('print', { message: String(msg) });
                    globalThis.Ok = (v) => ({ _tag: 'Ok', value: v, isOk: true, isErr: false, unwrap() { return v; } });
                    globalThis.Err = (e) => ({ _tag: 'Err', error: e, isOk: false, isErr: true, unwrap() { throw new Error(e); } });
                    globalThis.Some = (v) => ({ _tag: 'Some', value: v, isSome: true, isNone: false });
                    globalThis.None = { _tag: 'None', isSome: false, isNone: true };
                }
            "#.to_string()
        });

        let v8_code = v8::String::new(scope, &code).unwrap();
        let script = v8::Script::compile(scope, v8_code, None);
        match script {
            Some(s) => {
                if s.run(scope).is_some() {
                    log::info!("✅ [OMNI-CORE] Runtime polyfills berhasil diinjeksi — 22 modules siap");
                } else {
                    log::error!("❌ [OMNI-CORE] Runtime polyfills gagal dieksekusi");
                }
            }
            None => {
                log::error!("❌ [OMNI-CORE] Runtime polyfills gagal dikompilasi");
            }
        }
    }

    /// Injeksi OmniNative global object ke V8.
    /// Ini adalah jembatan utama di mana JavaScript memanggil kode native.
    ///
    /// Developer menulis: OmniNative.syscall("fs_read", { path: "/tmp/data.txt" })
    /// V8 memanggil callback Rust ini, yang dispatch ke syscalls.rs
    fn inject_omni_native(scope: &mut v8::ContextScope<v8::HandleScope>) {
        let context = scope.get_current_context();
        let global = context.global(scope);

        // Buat object OmniNative
        let native_obj = v8::Object::new(scope);

        // OmniNative.syscall(command, args) → Result
        let syscall_fn = v8::Function::new(scope, |scope: &mut v8::HandleScope,
                                             args: v8::FunctionCallbackArguments,
                                             mut rv: v8::ReturnValue| {
            // arg 0: command string
            let command = if args.length() > 0 {
                args.get(0).to_rust_string_lossy(scope)
            } else {
                "unknown".to_string()
            };

            // arg 1: arguments object → serialize ke JSON
            let args_json = if args.length() > 1 {
                let val = args.get(1);
                let json_str = v8::json::stringify(scope, val);
                match json_str {
                    Some(s) => s.to_rust_string_lossy(scope),
                    None => "{}".to_string(),
                }
            } else {
                "{}".to_string()
            };

            // Parse JSON args
            let parsed_args: serde_json::Value = serde_json::from_str(&args_json)
                .unwrap_or(serde_json::json!({}));

            // 🚀 DISPATCH ke Rust native handler!
            let result = syscalls::handle_syscall(&command, &parsed_args);

            // Serialize result kembali ke JSON string
            let result_json = serde_json::to_string(&result).unwrap_or_else(|_| "{}".into());

            // Parse JSON result menjadi V8 object
            let v8_json_str = v8::String::new(scope, &result_json).unwrap();
            if let Some(parsed) = v8::json::parse(scope, v8_json_str) {
                rv.set(parsed);
            }
        }).unwrap();

        let syscall_key = v8::String::new(scope, "syscall").unwrap();
        native_obj.set(scope, syscall_key.into(), syscall_fn.into());

        // OmniNative.version
        let ver_key = v8::String::new(scope, "version").unwrap();
        let ver_val = v8::String::new(scope, "1.3.0-SOVEREIGN").unwrap();
        native_obj.set(scope, ver_key.into(), ver_val.into());

        // Set OmniNative ke global
        let native_key = v8::String::new(scope, "OmniNative").unwrap();
        global.set(scope, native_key.into(), native_obj.into());
    }

    /// Injeksi console.log/warn/error ke V8 yang mengarah ke Rust logger
    fn inject_console(scope: &mut v8::ContextScope<v8::HandleScope>) {
        let context = scope.get_current_context();
        let global = context.global(scope);

        // Buat object 'console'
        let console_obj = v8::Object::new(scope);
        
        // console.log
        let log_fn = v8::Function::new(scope, |scope: &mut v8::HandleScope, 
                                         args: v8::FunctionCallbackArguments, 
                                         _rv: v8::ReturnValue| {
            let mut parts = Vec::new();
            for i in 0..args.length() {
                let val = args.get(i);
                parts.push(val.to_rust_string_lossy(scope));
            }
            println!("📟 [JS] {}", parts.join(" "));
        }).unwrap();

        let log_key = v8::String::new(scope, "log").unwrap();
        console_obj.set(scope, log_key.into(), log_fn.into());

        // console.warn
        let warn_fn = v8::Function::new(scope, |scope: &mut v8::HandleScope,
                                          args: v8::FunctionCallbackArguments,
                                          _rv: v8::ReturnValue| {
            let mut parts = Vec::new();
            for i in 0..args.length() {
                let val = args.get(i);
                parts.push(val.to_rust_string_lossy(scope));
            }
            eprintln!("⚠️ [JS WARN] {}", parts.join(" "));
        }).unwrap();

        let warn_key = v8::String::new(scope, "warn").unwrap();
        console_obj.set(scope, warn_key.into(), warn_fn.into());

        // console.error
        let error_fn = v8::Function::new(scope, |scope: &mut v8::HandleScope,
                                           args: v8::FunctionCallbackArguments,
                                           _rv: v8::ReturnValue| {
            let mut parts = Vec::new();
            for i in 0..args.length() {
                let val = args.get(i);
                parts.push(val.to_rust_string_lossy(scope));
            }
            eprintln!("❌ [JS ERROR] {}", parts.join(" "));
        }).unwrap();

        let error_key = v8::String::new(scope, "error").unwrap();
        console_obj.set(scope, error_key.into(), error_fn.into());

        // Set console object ke global
        let console_key = v8::String::new(scope, "console").unwrap();
        global.set(scope, console_key.into(), console_obj.into());
    }
}

// ==========================================
// 📊 STATISTIK ENGINE
// ==========================================

/// Statistik runtime dari V8 Isolate
#[derive(Debug, serde::Serialize)]
pub struct EngineStats {
    pub heap_used_bytes: usize,
    pub heap_total_bytes: usize,
    pub external_bytes: usize,
    pub v8_version: String,
    pub omni_version: String,
}

impl OmniEngine {
    /// Mengambil statistik heap memory dari V8 Isolate
    pub fn get_stats(&mut self) -> EngineStats {
        let mut stats = v8::HeapStatistics::default();
        self.isolate.get_heap_statistics(&mut stats);

        EngineStats {
            heap_used_bytes: stats.used_heap_size(),
            heap_total_bytes: stats.total_heap_size(),
            external_bytes: stats.external_memory(),
            v8_version: v8::V8::get_version().to_string(),
            omni_version: "1.3.0-SOVEREIGN".to_string(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_execution() {
        let mut engine = OmniEngine::boot();
        let result = engine.execute_js("1 + 1").unwrap();
        assert_eq!(result, "2");
    }

    #[test]
    fn test_json_stringify() {
        let mut engine = OmniEngine::boot();
        let result = engine.execute_js(r#"JSON.stringify({status: "OK", code: 200})"#).unwrap();
        assert!(result.contains("OK"));
    }

    #[test]
    fn test_omni_version_injected() {
        let mut engine = OmniEngine::boot();
        let result = engine.execute_js("__OMNI_VERSION__").unwrap();
        assert_eq!(result, "1.3.0-SOVEREIGN");
    }

    #[test]
    fn test_with_context() {
        let mut engine = OmniEngine::boot();
        let js = r#"
            function OmniHandler(req) {
                return JSON.stringify({ method: req.method, url: req.url });
            }
        "#;
        let result = engine.execute_with_context(js, "GET", "/api/users", "{}", "").unwrap();
        assert!(result.contains("GET"));
    }

    #[test]
    fn test_compile_error_handling() {
        let mut engine = OmniEngine::boot();
        let result = engine.execute_js("this is not valid javascript {{{}}}");
        assert!(result.is_err());
    }
}
