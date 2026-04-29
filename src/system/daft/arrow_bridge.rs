// OMNI Engine: Daft Apache Arrow Zero-Copy Integration
use std::sync::Arc;

pub struct ArrowBuffer {
    data: *const u8,
    len: usize,
}

unsafe impl Send for ArrowBuffer {}
unsafe impl Sync for ArrowBuffer {}

impl ArrowBuffer {
    /// Create a zero-copy wrapper around raw memory (e.g. from Python or C++)
    pub unsafe fn from_raw_parts(data: *const u8, len: usize) -> Self {
        ArrowBuffer { data, len }
    }

    pub fn as_slice(&self) -> &[u8] {
        unsafe { std::slice::from_raw_parts(self.data, self.len) }
    }
}

pub struct DaftSeries {
    pub name: String,
    pub buffer: Arc<ArrowBuffer>,
}

impl DaftSeries {
    pub fn new(name: &str, buffer: ArrowBuffer) -> Self {
        DaftSeries {
            name: name.to_string(),
            buffer: Arc::new(buffer),
        }
    }
}
