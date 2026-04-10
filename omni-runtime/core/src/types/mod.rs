// ==========================================
// ⚖️ OMNI-LANG TYPE SYSTEM: SANG HAKIM LOGIKA
// ==========================================
// Menerapkan "Gradual Typing" dengan kekuatan mutlak:
// 1. Any (Dynamic Typed - JS/Python style)
// 2. Strict (Statically Typed - Rust/C# style)
// 3. Null-Safe Mutlak (Swift/Kotlin style)
// 4. Matrix/Tensor Primitive (Julia/R style) untuk SIMD
// ==========================================

use serde::{Serialize, Deserialize};

pub mod vtable;

/// Kategori Tipe Data di OMNI
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum OmniType {
    /// Mode Prototipe Bebas (Python/JS): Kompilator menebak (Type Inference)
    Any,
    
    /// Primitif Kuat (Rust/C#)
    I32,
    I64,
    f32,
    f64,
    Boolean,
    String,
    
    /// Null-Safety Mutlak (Swift `String?`)
    /// Mencegah fatal error: "Cannot read property of undefined"
    Optional(Box<OmniType>),
    
    /// First-Class Scientific Data (Julia/R)
    /// Diterjemahkan langsung ke Instruksi SIMD (Single Instruction Multiple Data) di CPU GPU
    Matrix { rows: usize, cols: usize, element_type: Box<OmniType> },
    Tensor { dimensions: Vec<usize> },

    /// Custom Object / Struct
    Entity(String),
}

/// Representasi Nilai/Variabel di runtime OMNI
#[derive(Debug)]
pub struct OmniValue {
    pub declared_type: OmniType,
    pub is_null: bool,
    // Representasi raw bytes (disimulasikan sebagai string untuk saat ini)
    pub raw_data: String, 
}

impl OmniValue {
    pub fn new_dynamic(data: &str) -> Self {
        println!("[TYPE-SYSTEM] 🟡 Prototipe (Any): Inferring type for '{}'", data);
        Self {
            declared_type: OmniType::Any,
            is_null: false,
            raw_data: data.to_string(),
        }
    }

    pub fn new_strict_string(data: &str) -> Self {
        println!("[TYPE-SYSTEM] 🛡️ Strict Bound (String): Mutlak & Terkunci.");
        Self {
            declared_type: OmniType::String,
            is_null: false,
            raw_data: data.to_string(),
        }
    }

    pub fn new_optional(data: Option<&str>, inner_type: OmniType) -> Self {
        match data {
            Some(val) => {
                println!("[TYPE-SYSTEM] ❓ Optional Unwrapped (Safe): Memiliki nilai.");
                Self {
                    declared_type: OmniType::Optional(Box::new(inner_type)),
                    is_null: false,
                    raw_data: val.to_string(),
                }
            },
            None => {
                println!("[TYPE-SYSTEM] 🛑 Optional Null (SafeGuard): Tertangkap sebelum crash!");
                Self {
                    declared_type: OmniType::Optional(Box::new(inner_type)),
                    is_null: true,
                    raw_data: "NULL".to_string(),
                }
            }
        }
    }

    pub fn new_matrix(rows: usize, cols: usize, data: &str) -> Self {
        println!("[TYPE-SYSTEM] 🔬 Matrix Entity ({}x{}): Siap dikirim ke SIMD/ALU Tensor.", rows, cols);
        println!("[TYPE-SYSTEM]    Matriks bukan array biasa. Ini First-Class Citizen.");
        Self {
            declared_type: OmniType::Matrix { 
                rows, cols, element_type: Box::new(OmniType::f64) 
            },
            is_null: false,
            raw_data: data.to_string(),
        }
    }
}
