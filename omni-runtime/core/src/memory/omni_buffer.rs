use std::alloc::{alloc, dealloc, Layout};
use std::ptr::NonNull;

/// 🚀 OMNI ZERO-COPY MEMORY BUFFER (Arrow-like format)
/// Ini adalah struktur memori mentah yang melampaui batas bahasa.
/// Format data datar (flat) berkelanjutan yang disepakati oleh semua bahasa (C, C++, Rust, JS, Python, Go, dll).
/// Data TIDAK disalin ketika berpindah dari modul JavaScript ke komputasi Rust!
pub struct OmniBuffer {
    ptr: NonNull<u8>,
    len: usize,
    capacity: usize,
    layout: Layout,
}

impl OmniBuffer {
    /// Membuat struktur Zero-Copy baru.
    pub fn new(capacity: usize) -> Self {
        let layout = Layout::array::<u8>(capacity).expect("Gagal membuat memori layout");
        let ptr = unsafe { alloc(layout) };
        let ptr = NonNull::new(ptr).unwrap_or_else(|| std::alloc::handle_alloc_error(layout));

        println!("🧊 [OMNI-CELL] Zero-Copy Buffer {}-byte dialokasikan pada {:#x}", capacity, ptr.as_ptr() as usize);
        Self {
            ptr,
            len: 0,
            capacity,
            layout,
        }
    }

    /// Menambahkan data ke dalam buffer langsung tanpa struktur spesifik bahasa
    pub fn push_bytes(&mut self, data: &[u8]) {
        assert!(self.len + data.len() <= self.capacity, "Kapasitas OmniBuffer terlampaui!");
        unsafe {
            std::ptr::copy_nonoverlapping(data.as_ptr(), self.ptr.as_ptr().add(self.len), data.len());
        }
        self.len += data.len();
    }

    /// Mendapatkan alamat referensi RAW memori (64-bit pointer) yang bisa diloloskan ke `__omni_ffi` 
    pub fn as_raw_ptr(&self) -> *mut u8 {
        self.ptr.as_ptr()
    }

    pub fn length(&self) -> usize {
        self.len
    }
}

impl Drop for OmniBuffer {
    fn drop(&mut self) {
        println!("🔥 [OMNI-CELL] Membebaskan Zero-Copy Buffer pada {:#x}", self.ptr.as_ptr() as usize);
        unsafe {
            dealloc(self.ptr.as_ptr(), self.layout);
        }
    }
}
