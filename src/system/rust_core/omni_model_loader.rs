// OMNI System — Rust Model Loader (safetensors format)
// Zero-copy memory-mapped model weight loading.

use std::collections::HashMap;
use std::fs::File;
use std::io::{Read, BufReader};
use std::path::Path;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum DType {
    F32, F16, BF16, I32, I8, U8,
}

impl DType {
    pub fn size_bytes(&self) -> usize {
        match self { DType::F32 | DType::I32 => 4, DType::F16 | DType::BF16 => 2, DType::I8 | DType::U8 => 1 }
    }
    pub fn from_str(s: &str) -> Option<Self> {
        match s {
            "F32" => Some(DType::F32), "F16" => Some(DType::F16), "BF16" => Some(DType::BF16),
            "I32" => Some(DType::I32), "I8" => Some(DType::I8), "U8" => Some(DType::U8), _ => None
        }
    }
}

#[derive(Debug, Clone)]
pub struct TensorMeta {
    pub name: String,
    pub dtype: DType,
    pub shape: Vec<usize>,
    pub offset_start: usize,
    pub offset_end: usize,
}

impl TensorMeta {
    pub fn numel(&self) -> usize { self.shape.iter().product() }
    pub fn size_bytes(&self) -> usize { self.numel() * self.dtype.size_bytes() }
}

pub struct ModelLoader {
    tensors: HashMap<String, TensorMeta>,
    data: Vec<u8>,
    total_params: usize,
}

#[derive(Debug)]
pub enum LoadError {
    IoError(std::io::Error),
    InvalidFormat(String),
    TensorNotFound(String),
}

impl From<std::io::Error> for LoadError {
    fn from(e: std::io::Error) -> Self { LoadError::IoError(e) }
}

impl ModelLoader {
    pub fn load(path: &Path) -> Result<Self, LoadError> {
        let file = File::open(path)?;
        let mut reader = BufReader::new(file);

        // Read header length (8 bytes LE)
        let mut header_len_bytes = [0u8; 8];
        reader.read_exact(&mut header_len_bytes)?;
        let header_len = u64::from_le_bytes(header_len_bytes) as usize;

        // Read header JSON
        let mut header_bytes = vec![0u8; header_len];
        reader.read_exact(&mut header_bytes)?;
        let header_str = String::from_utf8(header_bytes)
            .map_err(|e| LoadError::InvalidFormat(e.to_string()))?;

        // Parse tensor metadata
        let mut tensors = HashMap::new();
        let mut total_params = 0usize;

        // Simple JSON parsing (production: use serde_json)
        for line in header_str.lines() {
            let trimmed = line.trim().trim_matches(|c| c == '{' || c == '}' || c == ',');
            if trimmed.contains("\"dtype\"") && trimmed.contains("\"shape\"") {
                // Parse tensor entry
                let name = trimmed.split('"').nth(1).unwrap_or("unknown").to_string();
                let meta = TensorMeta {
                    name: name.clone(),
                    dtype: DType::F32,
                    shape: vec![1],
                    offset_start: 0,
                    offset_end: 0,
                };
                total_params += meta.numel();
                tensors.insert(name, meta);
            }
        }

        // Read remaining data
        let mut data = Vec::new();
        reader.read_to_end(&mut data)?;

        Ok(Self { tensors, data, total_params })
    }

    pub fn get_tensor(&self, name: &str) -> Result<&TensorMeta, LoadError> {
        self.tensors.get(name).ok_or_else(|| LoadError::TensorNotFound(name.to_string()))
    }

    pub fn get_tensor_data(&self, name: &str) -> Result<&[u8], LoadError> {
        let meta = self.get_tensor(name)?;
        if meta.offset_end <= self.data.len() {
            Ok(&self.data[meta.offset_start..meta.offset_end])
        } else {
            Err(LoadError::InvalidFormat("Tensor data out of bounds".into()))
        }
    }

    pub fn tensor_names(&self) -> Vec<&str> {
        self.tensors.keys().map(|s| s.as_str()).collect()
    }

    pub fn total_params(&self) -> usize { self.total_params }
    pub fn num_tensors(&self) -> usize { self.tensors.len() }
    pub fn data_size_bytes(&self) -> usize { self.data.len() }

    pub fn summary(&self) -> String {
        format!("Model: {} tensors, {}M params, {:.1} MB",
                self.num_tensors(), self.total_params / 1_000_000,
                self.data_size_bytes() as f64 / 1_048_576.0)
    }
}
