// OMNI LIGHT RAG INDEX
// Domain: High Speed RAG Graph Retrieval
// Origin: HKUDS/LightRAG
use std::collections::HashMap;

#[derive(Debug)]
pub enum IndexError {
    KeyNotFound,
    IndexCorrupted,
}

pub struct LightRAGIndex {
    graph: HashMap<String, Vec<u8>>,
}

impl LightRAGIndex {
    pub fn new() -> Self {
        Self { graph: HashMap::new() }
    }

    pub fn insert_node(&mut self, key: String, vector: Vec<u8>) -> Result<(), IndexError> {
        self.graph.insert(key, vector);
        Ok(())
    }

    pub fn retrieve_nearest(&self, _query: &[u8]) -> Result<&Vec<u8>, IndexError> {
        self.graph.values().next().ok_or(IndexError::KeyNotFound)
    }
}\n