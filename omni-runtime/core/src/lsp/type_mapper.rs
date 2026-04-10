use super::uasg::UasgType;

/// Mesin Pemetakan Tipe Semantic (Cross-Language Semantic Type Mapper)
pub struct SemanticTypeMapper;

impl SemanticTypeMapper {
    /// Mengonversi Tipe Universal Graph (UASG) kembali ke bahasa *Editor Klien*.
    /// Misal ketika mengetik di TypeScript dan memanggil fungsi C++.
    pub fn translate_to(client_lang: &str, node_type: &UasgType) -> String {
        match client_lang {
            "typescript" | "javascript" => Self::to_typescript(node_type),
            "rust" => Self::to_rust(node_type),
            "cpp" => Self::to_cpp(node_type),
            "golang" => Self::to_golang(node_type),
            _ => "any".to_string(),
        }
    }

    fn to_typescript(t: &UasgType) -> String {
        match t {
            UasgType::String => "string".to_string(),
            UasgType::Int32 | UasgType::Int64 | UasgType::Float64 => "number".to_string(),
            UasgType::Boolean => "boolean".to_string(),
            UasgType::RawPointer => "SharedArrayBuffer /* OMNI-ABI */".to_string(),
            UasgType::Result(ok, err) => format!("{} | {}", Self::to_typescript(ok), Self::to_typescript(err)),
            UasgType::Void => "void".to_string(),
            UasgType::Custom(c) => c.clone(),
        }
    }

    fn to_rust(t: &UasgType) -> String {
        match t {
            UasgType::String => "String".to_string(),
            UasgType::Int32 => "i32".to_string(),
            UasgType::Int64 => "i64".to_string(),
            UasgType::Float64 => "f64".to_string(),
            UasgType::Boolean => "bool".to_string(),
            UasgType::RawPointer => "*mut u8".to_string(),
            UasgType::Result(ok, err) => format!("Result<{}, {}>", Self::to_rust(ok), Self::to_rust(err)),
            UasgType::Void => "()".to_string(),
            UasgType::Custom(c) => c.clone(),
        }
    }

    fn to_cpp(t: &UasgType) -> String {
        match t {
            UasgType::String => "std::string".to_string(),
            UasgType::Int32 => "int32_t".to_string(),
            UasgType::Int64 => "int64_t".to_string(),
            UasgType::Float64 => "double".to_string(),
            UasgType::Boolean => "bool".to_string(),
            UasgType::RawPointer => "omni::TensorView*".to_string(),
            UasgType::Result(ok, _) => format!("std::optional<{}>", Self::to_cpp(ok)), // Simplified mapping
            UasgType::Void => "void".to_string(),
            UasgType::Custom(c) => c.clone(),
        }
    }

    fn to_golang(t: &UasgType) -> String {
        match t {
            UasgType::String => "string".to_string(),
            UasgType::Int32 => "int32".to_string(),
            UasgType::Int64 => "int64".to_string(),
            UasgType::Float64 => "float64".to_string(),
            UasgType::Boolean => "bool".to_string(),
            UasgType::RawPointer => "unsafe.Pointer".to_string(),
            UasgType::Result(ok, _) => format!("({}, error)", Self::to_golang(ok)),
            UasgType::Void => "".to_string(),
            UasgType::Custom(c) => c.clone(),
        }
    }

    /// Linter Memori Real-Time Lintas Batas (Cross-Boundary Memory Linter)
    pub fn check_memory_leak_risk(source_lang: &str, target_lang: &str, node_type: &UasgType) -> Option<String> {
        // Mendeteksi bahaya: Bahasa Dinamis melempar pointer mentah ke C++ atau Rust
        let is_dynamic_to_native = (source_lang == "typescript" || source_lang == "javascript" || source_lang == "python")
                                    && (target_lang == "cpp" || target_lang == "rust");

        if is_dynamic_to_native {
            if let UasgType::RawPointer = node_type {
                return Some(
                    "Peringatan (OMNI-LSP): Objek Dinamis melewati Boundary via RawPointer ke ekosistem Bare-Metal. Pastikan fungsi tujuan tidak menahan pointer ini melampaui siklus eksekusi memori, atau panggil alloc_lock() untuk mencegah isu Garbage Collection!".to_string()
                );
            }
        }
        None
    }
}
