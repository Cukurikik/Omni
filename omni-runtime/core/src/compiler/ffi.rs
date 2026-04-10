// ==========================================
// 🔗 OMNI-LANG FFI: Zero-Overhead Foreign Function Interface
// ==========================================
// Menggantikan hack kotor `use::python` dan `use::c` dengan 
// decorator `@ffi` yang elegan dan di-lower langsung ke LLVM IR 
// `declare external` + `call` instructions.
//
// Sintaks OMNI:
//   @ffi(lib = "libsqlite3.so", language = "C")
//   extern fn sqlite3_open(filename: String, db: Pointer) -> Int;
//
// Output LLVM IR:
//   declare i32 @sqlite3_open(i8*, i8**)
// ==========================================

use super::ir::{OmniIR, OmniInstruction, IRType};

/// Metadata dari satu deklarasi @ffi decorator
#[derive(Debug, Clone)]
pub struct FFIBinding {
    pub func_name: String,
    pub lib_path: String,
    pub language: FFILanguage,
    pub params: Vec<FFIParam>,
    pub return_type: IRType,
    pub calling_convention: CallingConvention,
    pub gil_safe: bool,
}

#[derive(Debug, Clone, PartialEq)]
pub enum FFILanguage {
    C,
    Cpp,
    Python,
    Go,
    Rust,
}

impl FFILanguage {
    pub fn from_str(s: &str) -> Result<Self, String> {
        match s.to_lowercase().as_str() {
            "c" => Ok(FFILanguage::C),
            "c++" | "cpp" => Ok(FFILanguage::Cpp),
            "python" | "py" => Ok(FFILanguage::Python),
            "go" | "golang" => Ok(FFILanguage::Go),
            "rust" | "rs" => Ok(FFILanguage::Rust),
            _ => Err(format!("❌ FFI Error: Bahasa '{}' tidak didukung. Gunakan: C, C++, Python, Go, Rust", s)),
        }
    }
}

#[derive(Debug, Clone)]
pub enum CallingConvention {
    Cdecl,      // Default C ABI
    Stdcall,    // Windows API
    Fastcall,   // Register-based
    SysV,       // Linux/macOS x86_64
}

#[derive(Debug, Clone)]
pub struct FFIParam {
    pub name: String,
    pub ir_type: IRType,
}

/// The OMNI FFI Compiler — mengonversi @ffi decorator menjadi IR instructions
pub struct FFICompiler {
    bindings: Vec<FFIBinding>,
}

impl FFICompiler {
    pub fn new() -> Self {
        println!("[FFI] 🔗 OMNI Native FFI Compiler diaktifkan.");
        Self {
            bindings: Vec::new(),
        }
    }

    /// Parse @ffi decorator attributes dari AST dan register binding
    pub fn register_binding(
        &mut self,
        func_name: &str,
        lib_path: &str,
        language_str: &str,
        params: Vec<FFIParam>,
        return_type: IRType,
        gil_safe: bool,
    ) -> Result<(), String> {
        let language = FFILanguage::from_str(language_str)?;
        
        let calling_convention = match &language {
            FFILanguage::C | FFILanguage::Cpp => CallingConvention::Cdecl,
            FFILanguage::Go => CallingConvention::SysV,
            FFILanguage::Python => CallingConvention::Cdecl, // CPython uses C ABI
            FFILanguage::Rust => CallingConvention::SysV,
        };

        let binding = FFIBinding {
            func_name: func_name.to_string(),
            lib_path: lib_path.to_string(),
            language,
            params,
            return_type,
            calling_convention,
            gil_safe,
        };

        println!("[FFI] 📦 Registered: {} from {} (lang: {:?})", 
            binding.func_name, binding.lib_path, binding.language);
        
        self.bindings.push(binding);
        Ok(())
    }

    /// Lower semua FFI bindings menjadi OmniInstruction::FFIDeclare 
    pub fn emit_declarations(&self, ir: &mut OmniIR) {
        for binding in &self.bindings {
            ir.instructions.push(OmniInstruction::FFIDeclare {
                name: binding.func_name.clone(),
                lib: binding.lib_path.clone(),
                language: format!("{:?}", binding.language),
                params: binding.params.iter().map(|p| p.ir_type.clone()).collect(),
                ret: binding.return_type.clone(),
                gil_safe: binding.gil_safe,
            });
        }
    }

    /// Generate sebuah FFICall instruction
    pub fn emit_call(func_name: &str, args: Vec<String>, dest: &str) -> OmniInstruction {
        OmniInstruction::FFICall {
            dest: dest.to_string(),
            func_name: func_name.to_string(),
            args,
        }
    }

    /// Untuk Python FFI: generate GIL acquire/release wrapper
    pub fn generate_python_wrapper(binding: &FFIBinding) -> String {
        if binding.language != FFILanguage::Python {
            return String::new();
        }
        
        let mut wrapper = String::new();
        wrapper.push_str(&format!("; --- Python GIL Wrapper for {} ---\n", binding.func_name));
        wrapper.push_str("  %gil_state = call i32 @PyGILState_Ensure()\n");
        
        // Build argument list
        let args_str: Vec<String> = binding.params.iter().enumerate()
            .map(|(i, p)| format!("{} %arg{}", ir_type_to_llvm(&p.ir_type), i))
            .collect();
        
        wrapper.push_str(&format!("  %ffi_result = call {} @{}({})\n", 
            ir_type_to_llvm(&binding.return_type),
            binding.func_name,
            args_str.join(", ")
        ));
        
        wrapper.push_str("  call void @PyGILState_Release(i32 %gil_state)\n");
        wrapper.push_str("; --- End Python GIL Wrapper ---\n");
        
        wrapper
    }

    pub fn get_bindings(&self) -> &[FFIBinding] {
        &self.bindings
    }
}

/// Helper: Convert IRType ke LLVM IR type string
pub fn ir_type_to_llvm(ir_type: &IRType) -> String {
    match ir_type {
        IRType::Int64 => "i64".to_string(),
        IRType::Float64 => "double".to_string(),
        IRType::StringPtr => "i8*".to_string(),
        IRType::RenderNodePtr => "i8*".to_string(),
        IRType::MatrixPtr(rows, cols) => format!("[{} x [{} x double]]*", rows, cols),
        IRType::RawPtr => "i8*".to_string(),
    }
}
