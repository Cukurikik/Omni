/// OMNI TURBOPILOT: Memory Map Loader
/// Rust implementation for memory mapping (mmap) large local LLM weights directly into virtual memory.
/// Source: ravenscroftj/turbopilot

use std::fs::File;
use std::os::unix::io::AsRawFd;
use std::ptr;
use std::path::Path;

#[derive(Debug)]
pub enum MmapError {
    FileNotFound,
    MmapFailed,
}

pub struct ModelMmap {
    ptr: *mut libc::c_void,
    size: usize,
}

impl ModelMmap {
    /// Maps a model file into memory (Read Only, MAP_SHARED)
    pub fn new<P: AsRef<Path>>(path: P) -> Result<Self, MmapError> {
        let file = File::open(path).map_err(|_| MmapError::FileNotFound)?;
        let fd = file.as_raw_fd();
        
        let metadata = file.metadata().map_err(|_| MmapError::MmapFailed)?;
        let size = metadata.len() as usize;

        let ptr = unsafe {
            libc::mmap(
                ptr::null_mut(),
                size,
                libc::PROT_READ,
                libc::MAP_SHARED,
                fd,
                0,
            )
        };

        if ptr == libc::MAP_FAILED {
            return Err(MmapError::MmapFailed);
        }

        // Madvise to let OS know we will read sequentially (helps edge devices)
        unsafe {
            libc::madvise(ptr, size, libc::MADV_SEQUENTIAL);
        }

        Ok(ModelMmap { ptr, size })
    }

    pub fn get_slice(&self) -> &[u8] {
        unsafe { std::slice::from_raw_parts(self.ptr as *const u8, self.size) }
    }
}

impl Drop for ModelMmap {
    fn drop(&mut self) {
        unsafe {
            libc::munmap(self.ptr, self.size);
        }
    }
}
