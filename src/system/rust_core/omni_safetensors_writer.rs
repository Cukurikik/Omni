// OMNI System — Rust Safetensors Serializer
// Write model weights in safetensors format.

use std::collections::HashMap;
use std::io::Write;

pub struct SafetensorsMeta {
    pub name: String,
    pub dtype: String,
    pub shape: Vec<usize>,
    pub data_offset: usize,
    pub data_length: usize,
}

pub struct SafetensorsWriter {
    tensors: Vec<(SafetensorsMeta, Vec<u8>)>,
}

impl SafetensorsWriter {
    pub fn new() -> Self { Self { tensors: Vec::new() } }

    pub fn add_f32(&mut self, name: &str, shape: &[usize], data: &[f32]) {
        let bytes: Vec<u8> = data.iter().flat_map(|f| f.to_le_bytes()).collect();
        let meta = SafetensorsMeta {
            name: name.to_string(), dtype: "F32".to_string(),
            shape: shape.to_vec(), data_offset: 0, data_length: bytes.len(),
        };
        self.tensors.push((meta, bytes));
    }

    pub fn add_f16_from_f32(&mut self, name: &str, shape: &[usize], data: &[f32]) {
        let bytes: Vec<u8> = data.iter().flat_map(|f| {
            let bits = f.to_bits();
            let sign = (bits >> 31) & 1;
            let exp = ((bits >> 23) & 0xFF) as i32 - 127 + 15;
            let mantissa = (bits >> 13) & 0x3FF;
            let h = if exp <= 0 { 0u16 } else if exp >= 31 { (sign as u16) << 15 | 0x7C00 }
                    else { (sign as u16) << 15 | (exp as u16) << 10 | mantissa as u16 };
            h.to_le_bytes()
        }).collect();
        let meta = SafetensorsMeta {
            name: name.to_string(), dtype: "F16".to_string(),
            shape: shape.to_vec(), data_offset: 0, data_length: bytes.len(),
        };
        self.tensors.push((meta, bytes));
    }

    pub fn write_to_file(&self, path: &str) -> Result<usize, std::io::Error> {
        let mut header_map = HashMap::new();
        let mut offset = 0usize;
        for (meta, data) in &self.tensors {
            let entry = format!(
                "\"{}\":{{\"dtype\":\"{}\",\"shape\":[{}],\"data_offsets\":[{},{}]}}",
                meta.name, meta.dtype,
                meta.shape.iter().map(|s| s.to_string()).collect::<Vec<_>>().join(","),
                offset, offset + data.len()
            );
            header_map.insert(meta.name.clone(), entry);
            offset += data.len();
        }

        let header_content = format!("{{{}}}", 
            header_map.values().cloned().collect::<Vec<_>>().join(","));
        let header_bytes = header_content.as_bytes();
        let header_len = header_bytes.len() as u64;

        let mut file = std::fs::File::create(path)?;
        file.write_all(&header_len.to_le_bytes())?;
        file.write_all(header_bytes)?;
        for (_, data) in &self.tensors { file.write_all(data)?; }

        let total = 8 + header_bytes.len() + offset;
        Ok(total)
    }

    pub fn num_tensors(&self) -> usize { self.tensors.len() }
    pub fn total_bytes(&self) -> usize { self.tensors.iter().map(|(_, d)| d.len()).sum() }
}
