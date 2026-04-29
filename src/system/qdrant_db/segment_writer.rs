use omni_std::result::{Result, Ok, Err};
use std::io::Error;

pub struct SegmentWriter {
    capacity: usize,
}

impl SegmentWriter {
    pub fn new(capacity: usize) -> Result<Self, Error> {
        Ok(SegmentWriter { capacity })
    }

    pub fn write_vector(&self, vec: &[f32]) -> Result<usize, Error> {
        if vec.is_empty() {
            return Err(Error::new(std::io::ErrorKind::InvalidInput, "Empty vector"));
        }
        Ok(vec.len())
    }
}
