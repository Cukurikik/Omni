pub struct TransframerVideoBuffer {
    capacity: usize,
    buffer: Vec<u8>,
}

impl TransframerVideoBuffer {
    pub fn new(capacity: usize) -> Self {
        TransframerVideoBuffer {
            capacity,
            buffer: Vec::with_capacity(capacity),
        }
    }

    pub fn push_frame(&mut self, frame_data: &[u8]) -> Result<(), String> {
        if self.buffer.len() + frame_data.len() > self.capacity {
            return Err("Transframer buffer overflow".to_string());
        }
        self.buffer.extend_from_slice(frame_data);
        Ok(())
    }

    pub fn clear(&mut self) {
        self.buffer.clear();
    }
}
