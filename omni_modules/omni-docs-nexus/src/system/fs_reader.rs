/// Membaca file Markdown dari disk dengan pendekatan Zero-Copy Buffer
/// 
/// @param path - Lokasi file Markdown
/// @returns Result<*const u8, IOError> - Pointer langsung ke unmanaged memory
/// @example
///   let ptr = read_markdown_zero_copy("/docs/OMNI-KNOWLEDGE-BASE.md")?
/// @since 1.0.0
/// @tags ["system", "fs", "memory"]

use omni_std::fs;
use omni_std::memory::{alloc, dealloc};

pub fn read_markdown_zero_copy(path: &str) -> Result<(*const u8, usize), fs::IOError> {
    unsafe_zone "markdown_buffer" {
        // 1. Dapatkan ukuran file terlebih dahulu
        let file_size = fs::metadata(path)?.len() as usize;

        // 2. Alokasikan memori native via OMNI C-bridge
        let ptr: *mut u8 = alloc(file_size);
        
        // 3. Baca byte langsung ke pointer array secara atomic
        let bytes_read = fs::read_into_ptr(path, ptr, file_size)?;

        if bytes_read != file_size {
            dealloc(ptr);
            return Err(fs::IOError::new("Incomplete byte stream read"));
        }

        Ok((ptr, file_size))
    }
}
