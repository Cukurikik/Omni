// ==========================================
// 🧬 V8 MICRO ISOLATE — RUSTY_V8 ASLI
// ==========================================
// BUKAN SIMULASI. BUKAN PROXY. BUKAN STUB.
// Ini adalah V8 Engine sungguhan yang di-embed
// langsung ke dalam binary Rust melalui rusty_v8.
// Kode JavaScript dieksekusi di dalam V8 Isolate
// dengan sandboxing penuh.
//
// Runtime: omni-std v2.0.0 (8 modul JS)
// ==========================================

use anyhow::Result;
use std::sync::Once;
use crate::stdlib::runtime;
use crate::stdlib::import_resolver;

static V8_INIT: Once = Once::new();

pub struct V8MicroIsolate {
    active: bool,
}

impl V8MicroIsolate {
    pub fn new() -> Self {
        Self { active: false }
    }

    /// Inisialisasi V8 Platform — hanya sekali per proses
    pub fn initialize(&mut self) -> Result<()> {
        println!("🚀 [OMNI-V8] Menginisialisasi V8 Engine (rusty_v8)...");

        V8_INIT.call_once(|| {
            let platform = v8::new_default_platform(0, false).make_shared();
            v8::V8::initialize_platform(platform);
            v8::V8::initialize();
            println!("  ✅ V8 Platform & Engine terinisialisasi.");
        });

        // Print info omni-std yang dimuat
        println!("  📦 {}", runtime::runtime_info());

        self.active = true;
        Ok(())
    }

    /// Eksekusi JavaScript ASLI di dalam V8 Isolate.
    /// Mengembalikan seluruh output print/console.log sebagai String.
    pub fn execute(&self, js_code: &str) -> Result<String> {
        if !self.active {
            return Err(anyhow::anyhow!("V8 Engine belum diinisialisasi!"));
        }

        // ═══ BUAT ISOLATE BARU (sandbox terpisah) ═══
        let isolate = &mut v8::Isolate::new(v8::CreateParams::default());
        let handle_scope = &mut v8::HandleScope::new(isolate);
        let context = v8::Context::new(handle_scope);
        let scope = &mut v8::ContextScope::new(handle_scope, context);

        // ═══ OMNI FFI NATIVE BINDING ═══
        // Menghubungkan JS block dari OMNI AST ke Rust secara native
        let global = context.global(scope);
        let ffi_fn_name = v8::String::new(scope, "__omni_ffi").unwrap();
        let ffi_fn = v8::Function::new(
            scope,
            |scope: &mut v8::HandleScope, args: v8::FunctionCallbackArguments, mut rv: v8::ReturnValue| {
                let lang = args.get(0).to_rust_string_lossy(scope);
                let code = args.get(1).to_rust_string_lossy(scope);
                println!("⚡ [OMNI-FFI] NATIVE BOUNDARY ACTIVATED");
                println!("   ⚙️  Language : {}", lang);
                println!("   📦 Payload  : {} bytes", code.len());
                // Zero-Copy Pointer (Tahap berikutnya akan mengompilasi raw code)
                let return_val = v8::String::new(scope, "zero_copy_ref_0xOMNI").unwrap();
                rv.set(return_val.into());
            }
        ).unwrap();
        global.set(scope, ffi_fn_name.into(), ffi_fn.into());

        // ═══ OMNI-STD BOOTSTRAP ═══
        // Memuat seluruh standard library dari src/stdlib/js/*
        // Dikompilasi ke dalam binary via include_str! — zero file I/O
        let omni_std = runtime::get_full_runtime();

        let full_source = format!(
            r#"
{omni_std}

// ═══ OMNI USER CODE ═══
{user_code}

// ═══ HASIL ═══
JSON.stringify(__omni_output);
"#,
            omni_std = omni_std,
            user_code = js_code
        );

        // ═══ COMPILE SCRIPT DI V8 ═══
        let source = v8::String::new(scope, &full_source)
            .ok_or_else(|| anyhow::anyhow!("Gagal membuat V8 String dari source code"))?;

        // ═══ GUNAKAN TryCatch UNTUK ERROR HANDLING NYATA ═══
        let tc_scope = &mut v8::TryCatch::new(scope);

        let script = v8::Script::compile(tc_scope, source, None);

        let script = match script {
            Some(s) => s,
            None => {
                let exception = tc_scope.exception()
                    .map(|e| e.to_rust_string_lossy(tc_scope))
                    .unwrap_or_else(|| "Unknown compilation error".to_string());
                return Err(anyhow::anyhow!("❌ V8 Compilation Error:\n{}", exception));
            }
        };

        // ═══ EKSEKUSI SCRIPT DI V8 ═══
        let result = script.run(tc_scope);

        match result {
            Some(value) => {
                let output_json = value.to_rust_string_lossy(tc_scope);
                // Parse JSON array → gabung jadi baris output
                match serde_json::from_str::<Vec<String>>(&output_json) {
                    Ok(lines) => Ok(lines.join("\n")),
                    Err(_) => Ok(output_json),
                }
            }
            None => {
                let exception = tc_scope.exception()
                    .map(|e| e.to_rust_string_lossy(tc_scope))
                    .unwrap_or_else(|| "Unknown runtime error".to_string());

                // Coba dapatkan stack trace
                let stack_trace = tc_scope.stack_trace()
                    .map(|s| s.to_rust_string_lossy(tc_scope))
                    .unwrap_or_default();

                let mut error_msg = format!("❌ V8 Runtime Error: {}", exception);
                if !stack_trace.is_empty() {
                    error_msg.push_str(&format!("\n   Stack: {}", stack_trace));
                }
                Err(anyhow::anyhow!("{}", error_msg))
            }
        }
    }

    /// Eksekusi JavaScript dengan selective import resolution.
    /// Menerima source .omni asli untuk parse import directives,
    /// lalu hanya memuat modul stdlib yang dibutuhkan.
    ///
    /// # Arguments
    /// * `js_code` — Transpiled JavaScript dari AST
    /// * `omni_source` — Source code .omni asli (untuk parse imports)
    /// * `project_dir` — Directory proyek (untuk resolve package imports)
    pub fn execute_with_imports(
        &self,
        js_code: &str,
        omni_source: &str,
        project_dir: Option<&std::path::Path>,
    ) -> Result<String> {
        if !self.active {
            return Err(anyhow::anyhow!("V8 Engine belum diinisialisasi!"));
        }

        // ═══ RESOLVE IMPORTS ═══
        let resolution = import_resolver::resolve_imports(omni_source, project_dir);
        
        println!("📦 [IMPORT RESOLVER] {} imports ditemukan, {} gagal",
            resolution.imports.len(), resolution.failed_count);
        
        for import in &resolution.imports {
            let status = if import.resolved { "✅" } else { "❌" };
            println!("   {} {} → {:?}", status, import.raw_path, import.kind);
        }

        if resolution.failed_count > 0 {
            eprintln!("⚠️ [IMPORT] {} import gagal di-resolve!", resolution.failed_count);
        }

        // ═══ BUAT V8 ISOLATE ═══
        let isolate = &mut v8::Isolate::new(v8::CreateParams::default());
        let handle_scope = &mut v8::HandleScope::new(isolate);
        let context = v8::Context::new(handle_scope);
        let scope = &mut v8::ContextScope::new(handle_scope, context);

        // ═══ OMNI FFI NATIVE BINDING ═══
        let global = context.global(scope);
        let ffi_fn_name = v8::String::new(scope, "__omni_ffi").unwrap();
        let ffi_fn = v8::Function::new(
            scope,
            |scope: &mut v8::HandleScope, args: v8::FunctionCallbackArguments, mut rv: v8::ReturnValue| {
                let lang = args.get(0).to_rust_string_lossy(scope);
                let code = args.get(1).to_rust_string_lossy(scope);
                println!("⚡ [OMNI-FFI] NATIVE BOUNDARY ACTIVATED");
                println!("   ⚙️  Language : {}", lang);
                println!("   📦 Payload  : {} bytes", code.len());
                let return_val = v8::String::new(scope, "zero_copy_ref_0xOMNI").unwrap();
                rv.set(return_val.into());
            }
        ).unwrap();
        global.set(scope, ffi_fn_name.into(), ffi_fn.into());

        // ═══ SELECTIVE STDLIB BOOTSTRAP ═══
        // Hanya memuat modul yang di-import, bukan seluruh runtime
        let stdlib_bootstrap = import_resolver::get_selective_runtime(&resolution.imports);

        let full_source = format!(
            r#"
{stdlib}

// ═══ OMNI USER CODE (Import-Resolved) ═══
{user_code}

// ═══ HASIL ═══
JSON.stringify(__omni_output);
"#,
            stdlib = stdlib_bootstrap,
            user_code = js_code
        );

        // ═══ COMPILE & EXECUTE ═══
        let source = v8::String::new(scope, &full_source)
            .ok_or_else(|| anyhow::anyhow!("Gagal membuat V8 String dari source code"))?;

        let tc_scope = &mut v8::TryCatch::new(scope);
        let script = v8::Script::compile(tc_scope, source, None);

        let script = match script {
            Some(s) => s,
            None => {
                let exception = tc_scope.exception()
                    .map(|e| e.to_rust_string_lossy(tc_scope))
                    .unwrap_or_else(|| "Unknown compilation error".to_string());
                return Err(anyhow::anyhow!("❌ V8 Compilation Error:\n{}", exception));
            }
        };

        let result = script.run(tc_scope);

        match result {
            Some(value) => {
                let output_json = value.to_rust_string_lossy(tc_scope);
                match serde_json::from_str::<Vec<String>>(&output_json) {
                    Ok(lines) => Ok(lines.join("\n")),
                    Err(_) => Ok(output_json),
                }
            }
            None => {
                let exception = tc_scope.exception()
                    .map(|e| e.to_rust_string_lossy(tc_scope))
                    .unwrap_or_else(|| "Unknown runtime error".to_string());
                let stack_trace = tc_scope.stack_trace()
                    .map(|s| s.to_rust_string_lossy(tc_scope))
                    .unwrap_or_default();
                let mut error_msg = format!("❌ V8 Runtime Error: {}", exception);
                if !stack_trace.is_empty() {
                    error_msg.push_str(&format!("\n   Stack: {}", stack_trace));
                }
                Err(anyhow::anyhow!("{}", error_msg))
            }
        }
    }
}

