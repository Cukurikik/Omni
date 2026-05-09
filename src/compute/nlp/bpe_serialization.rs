//=============================================================================
// OMNI SYSTEM LAYER — BPE SERIALIZATION (RUST)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: Memory-safe, zero-copy serialization/deserialization of massive 
//              Byte-Pair Encoding vocabularies.
//=============================================================================

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs::File;
use std::io::{Read, Write};
use bincode;

#[derive(Serialize, Deserialize, Debug)]
pub struct BpeVocab {
    pub vocab_size: usize,
    pub token_to_id: HashMap<String, u32>,
    pub id_to_token: HashMap<u32, String>,
    pub merges: Vec<(String, String)>,
}

pub enum BpeError {
    IoError(std::io::Error),
    SerializationError(bincode::Error),
}

impl BpeVocab {
    pub fn save_to_disk(&self, filepath: &str) -> Result<(), BpeError> {
        let mut file = File::create(filepath).map_err(BpeError::IoError)?;
        
        // Fast binary serialization
        let encoded: Vec<u8> = bincode::serialize(self).map_err(BpeError::SerializationError)?;
        
        file.write_all(&encoded).map_err(BpeError::IoError)?;
        Ok(())
    }

    pub fn load_from_disk(filepath: &str) -> Result<Self, BpeError> {
        let mut file = File::open(filepath).map_err(BpeError::IoError)?;
        let mut buffer = Vec::new();
        
        file.read_to_end(&mut buffer).map_err(BpeError::IoError)?;
        
        let decoded: Self = bincode::deserialize(&buffer).map_err(BpeError::SerializationError)?;
        Ok(decoded)
    }
}
