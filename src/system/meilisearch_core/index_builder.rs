use omni_std::result::{Result, Ok, Err};

pub struct IndexBuilder;

impl IndexBuilder {
    pub fn build_index(data: &[u8]) -> Result<bool, String> {
        if data.is_empty() {
            return Err("Data is empty".to_string());
        }
        Ok(true)
    }
}
