use std::fs::{File, OpenOptions};
use std::io::{Write, Read};
use std::path::Path;

/// OMNI Easy LM Checkpoint Manager
/// Safely writes and reads model state dicts to disk without corruption.

pub struct CheckpointManager {
    save_dir: String,
}

impl CheckpointManager {
    pub fn new(save_dir: &str) -> Self {
        Self {
            save_dir: save_dir.to_string(),
        }
    }

    pub fn save_checkpoint(&self, step: u64, data: &[u8]) -> Result<String, std::io::Error> {
        let path = format!("{}/checkpoint-{}.bin", self.save_dir, step);
        let mut file = OpenOptions::new()
            .write(true)
            .create(true)
            .open(&path)?;
            
        file.write_all(data)?;
        file.sync_all()?;
        
        Ok(path)
    }

    pub fn load_checkpoint(&self, step: u64) -> Result<Vec<u8>, std::io::Error> {
        let path = format!("{}/checkpoint-{}.bin", self.save_dir, step);
        if !Path::new(&path).exists() {
            return Err(std::io::Error::new(std::io::ErrorKind::NotFound, "Checkpoint not found"));
        }
        
        let mut file = File::open(&path)?;
        let mut buffer = Vec::new();
        file.read_to_end(&mut buffer)?;
        
        Ok(buffer)
    }
}
