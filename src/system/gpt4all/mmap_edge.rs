/// OMNI GPT4ALL: Memory Mapped Loader (Edge)
/// Rust implementation for loading quantized model files into memory on resource-constrained devices.
/// Source: nomic-ai/gpt4all

use std::fs::File;
use std::os::unix::io::AsRawFd;
use std::ptr;

pub enum MmapError {
    FileNotFound,
    FileMetadataError,
    MmapFailed,
}

pub struct EdgeModelMmap {
    ptr: *mut libc::c_void,
    size: usize,
    _file: File, // Keep file open while mapped
}

impl EdgeModelMmap {
    pub fn new(path: &str) -> Result<Self, MmapError> {
        let file = File::open(path).map_err(|_| MmapError::FileNotFound)?;
        let metadata = file.metadata().map_err(|_| MmapError::FileMetadataError)?;
        let size = metadata.len() as usize;

        if size == 0 {
            return Err(MmapError::FileMetadataError);
        }

        let fd = file.as_raw_fd();
        
        // MAP_SHARED allows multiple processes to share the physical memory
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

        // Hint to the OS kernel that we'll be randomly accessing this memory (typical for LLM inference)
        unsafe {
            libc::madvise(ptr, size, libc::MADV_RANDOM);
        }

        Ok(EdgeModelMmap {
            ptr,
            size,
            _file: file,
        })
    }

    pub fn as_slice(&self) -> &[u8] {
        unsafe { std::slice::from_raw_parts(self.ptr as *const u8, self.size) }
    }
}

impl Drop for EdgeModelMmap {
    fn drop(&mut self) {
        if !self.ptr.is_null() && self.ptr != libc::MAP_FAILED {
            unsafe {
                libc::munmap(self.ptr, self.size);
            }
        }
    }
}
