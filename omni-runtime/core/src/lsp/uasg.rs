use std::collections::HashMap;

/// Tipe Data Dasar Generic lintas bahasa
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum UasgType {
    String,
    Int32,
    Int64,
    Float64,
    Boolean,
    RawPointer,      // *mut u8 / uintptr_t
    Result(Box<UasgType>, Box<UasgType>),
    Void,
    Custom(String),
}

/// Node Graph mewakili satu entitas di seluruh ekosistem kompilasi
#[derive(Debug, Clone)]
pub struct UasgNode {
    pub id: String,                    // Misalnya: "project::module::function_name"
    pub original_lang: String,         // "rust", "typescript", "cpp"
    pub location_file: String,         // "src/main.rs"
    pub location_line: u32,
    pub node_type: UasgNodeType,
}

#[derive(Debug, Clone)]
pub enum UasgNodeType {
    Function {
        params: Vec<(String, UasgType)>, // nama parameter, tipe
        return_type: UasgType,
        is_async: bool,
    },
    Class {
        methods: Vec<String>, // Referensi ID ke UasgNode Fungsi
        properties: HashMap<String, UasgType>,
    },
    Variable {
        var_type: UasgType,
        is_mutable: bool,
    }
}

/// Penyimpan Terpusat AST Multi-Language yang disimpan Daemon di RAM
pub struct UnifiedAbstractSyntaxGraph {
    pub nodes: HashMap<String, UasgNode>,
}

impl UnifiedAbstractSyntaxGraph {
    pub fn new() -> Self {
        Self { nodes: HashMap::new() }
    }

    /// Menambahkan entitas bahasa (contoh hasil tangkapan parser) ke Graph
    pub fn register_node(&mut self, node: UasgNode) {
        self.nodes.insert(node.id.clone(), node);
    }

    /// Menyediakan insight (Go To Def, Hover) merujuk Node manapun
    pub fn find_node(&self, partial_id: &str) -> Option<&UasgNode> {
        self.nodes.values().find(|n| n.id.contains(partial_id))
    }
}
