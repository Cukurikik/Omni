// ==========================================
// 🌉 OMNI-IR: Static Single Assignment (SSA)
// ==========================================
// Intermediate Representation tempat di mana 16 bahasa pecah
// menjadi satu format instruksi linier rendah yang aman.
// OMNI-IR menggunakan format SSA (semua variabel didefinisikan sekali).
// ==========================================

#[derive(Debug, Clone, PartialEq)]
pub enum IRType {
    Int64,
    Float64,
    StringPtr,
    /// Alokasi memori grafik untuk Engine Flutter/HTML rendering
    RenderNodePtr,
    /// Representasi memori contiguous (SIMD-ready)
    MatrixPtr(usize, usize), 
    /// Representasi pointer tanpa GC
    RawPtr,
}

#[derive(Debug, Clone)]
pub enum OmniInstruction {
    /// Dilema UI: Merubah Deklarasi UI menjadi instruksi Graph Alokasi
    AllocRenderTree {
        dest: String, // SSA v0, v1
        tag: String,
    },
    /// Dilema Tipe: Zero-Cost Abstraction untuk Generic Types
    MonomorphizedCall {
        dest: String,
        func_name_mangled: String,
        args: Vec<String>,
    },
    /// Dilema Data: Menghancurkan loop matrix menjadi 1 instruksi Vector
    SimdMultiply {
        dest: String,
        left_matrix_ptr: String,
        right_matrix_ptr: String,
    },
    /// Dilema Konkurensi: Meruntuhkan callback Async menjadi state machine background
    SpawnStateMachine {
        dest: String,
        state_id: usize,
        func_ptr: String,
    },

    // Operasi Standar
    LoadConstantInt { dest: String, value: i64 },
    LoadConstantFloat { dest: String, value: f64 },
    Add { dest: String, left: String, right: String },
    MemoryAlloc { dest: String, size_bytes: usize },
    MemoryFree { ptr: String },

    // ==========================================
    // 🔗 FFI (Foreign Function Interface) Instructions
    // ==========================================

    /// Deklarasi fungsi external dari library C/Python/Go
    /// Lowered ke LLVM IR `declare` statement
    FFIDeclare {
        name: String,
        lib: String,             // e.g. "libsqlite3.so"
        language: String,        // "C", "Python", "Go"
        params: Vec<IRType>,
        ret: IRType,
        gil_safe: bool,          // Untuk Python: apakah GIL-safe?
    },

    /// Pemanggilan fungsi foreign yang sudah di-declare
    /// Lowered ke LLVM IR `call` instruction
    FFICall {
        dest: String,
        func_name: String,
        args: Vec<String>,
    },
}

pub struct OmniIR {
    pub instructions: Vec<OmniInstruction>,
}

impl OmniIR {
    pub fn new() -> Self {
        println!("[OMNI-IR] 🌉 Struktur SSA (Static Single Assignment) OMNI-IR Aktif.");
        Self {
            instructions: Vec::new(),
        }
    }

    pub fn to_string(&self) -> String {
        let mut output = String::new();
        for inst in &self.instructions {
            output.push_str(&format!("{:?}\n", inst));
        }
        output
    }
}
