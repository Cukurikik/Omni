// ============================================================
// OMNI Rust Client Bridge — User-Land SDK
// ============================================================
// Layer: System (untuk pengguna Rust yang mengkonsumsi OMNI as lib)
// Crate ini TIDAK perlu cargo add apapun — pure Rust std.
// ============================================================

use std::ffi::c_void;

extern "C" {
    fn __omni_ffi(args_buffer: *const u8, len: usize) -> *mut u8;
    fn __omni_buffer_alloc(size: usize) -> *mut u8;
    fn __omni_buffer_free(ptr: *mut u8, len: usize);
}

/// Monadic Result khusus OMNI
pub type OmniResult<T> = Result<T, OmniError>;

/// Error bertipe dari kernel
#[derive(Debug)]
pub struct OmniError {
    pub code: &'static str,
    pub message: String,
}

impl std::fmt::Display for OmniError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "[{}] {}", self.code, self.message)
    }
}

impl std::error::Error for OmniError {}

/// Managed buffer yang otomatis di-dealloc (RAII)
pub struct OmniBuffer {
    ptr: *mut u8,
    len: usize,
}

impl OmniBuffer {
    /// Alokasi buffer baru di OMNI heap
    pub fn alloc(size: usize) -> OmniResult<Self> {
        let ptr = unsafe { __omni_buffer_alloc(size) };
        if ptr.is_null() {
            return Err(OmniError {
                code: "E091",
                message: "Buffer allocation failed".into(),
            });
        }
        Ok(Self { ptr, len: size })
    }

    /// Akses slice immutable
    pub fn as_slice(&self) -> &[u8] {
        unsafe { std::slice::from_raw_parts(self.ptr, self.len) }
    }

    /// Akses slice mutable
    pub fn as_mut_slice(&mut self) -> &mut [u8] {
        unsafe { std::slice::from_raw_parts_mut(self.ptr, self.len) }
    }

    pub fn len(&self) -> usize {
        self.len
    }

    pub fn is_empty(&self) -> bool {
        self.len == 0
    }
}

impl Drop for OmniBuffer {
    fn drop(&mut self) {
        if !self.ptr.is_null() {
            unsafe { __omni_buffer_free(self.ptr, self.len) };
        }
    }
}

/// Eksekusi fungsi OMNI dari user-land Rust
pub fn execute(data: &[u8]) -> OmniResult<*mut u8> {
    if data.is_empty() {
        return Err(OmniError {
            code: "E092",
            message: "Data tidak boleh kosong".into(),
        });
    }

    let result = unsafe { __omni_ffi(data.as_ptr(), data.len()) };

    if result.is_null() {
        return Err(OmniError {
            code: "E093",
            message: "Kernel mengembalikan null pointer".into(),
        });
    }

    Ok(result)
}
