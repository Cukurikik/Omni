use libloading::{Library, Symbol};
use std::collections::HashMap;
use std::ffi::CString;

/// 🌌 OMNI TRANSPARENT FFI (Dynamic Auto-Binder)
/// Solusi "Sindrom Kota Hantu".
/// Fitur ini memungkinkan OMNI untuk me-load `.dll` (Win), `.so` (Linux), atau `.dylib` (Mac)
/// tanpa memerlukan file C-Header atau Rust-Bindings yang dibuat secara manual.
pub struct OmniDynamicLoader {
    libraries: HashMap<String, Library>,
}

impl OmniDynamicLoader {
    pub fn new() -> Self {
        println!("🚀 [OMNI-LINK] Transparent FFI Engine Online. Siap melahap native binary.");
        Self {
            libraries: HashMap::new(),
        }
    }

    /// Membaca file dynamic library secara runtime
    pub unsafe fn load_native_library(&mut self, path: &str, alias: &str) -> Result<(), libloading::Error> {
        let lib_path = CString::new(path).unwrap();
        // Load library directly
        let lib = Library::new(lib_path.to_str().unwrap())?;
        println!("✅ [OMNI-LINK] Native Library '{}' sukses diload sebagai akses OMNI.", path);
        self.libraries.insert(alias.to_string(), lib);
        Ok(())
    }

    /// Mengeksekusi fungsi arbitrer dari native library dengan argumen raw
    /// Fungsi ini menerima OmniBuffer raw pointer (64-bit int) untuk argumen dan return
    pub unsafe fn execute_native_symbol<T>(
        &self, 
        lib_alias: &str, 
        symbol_name: &str, 
        arg_ptr: *mut u8
    ) -> Result<T, String> {
        let lib = self.libraries.get(lib_alias).ok_or("Library belum di load!")?;
        let symbol_c = CString::new(symbol_name).unwrap();
        
        // Asumsikan semua fungsi OMNI FFI mengambil *mut u8 dan mereturn custom T 
        // yang compatible (seperti memori Arrow)
        let func: Symbol<unsafe extern "C" fn(*mut u8) -> T> = lib
            .get(symbol_c.as_bytes_with_nul())
            .map_err(|e| format!("Symbol not found: {}", e))?;
            
        println!("⚡ [OMNI-LINK] Mengeksekusi symbol OMNI-C ABI '{}' pada library '{}'", symbol_name, lib_alias);
        Ok(func(arg_ptr))
    }
}
