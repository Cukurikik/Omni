// ============================================================
// ⚡ omni-std/system/memory.rs — OMNI Native Memory Core
// ============================================================

#![allow(non_camel_case_types)]
use std::alloc::{alloc, dealloc, Layout};
use std::ptr;

// ─── OMNI Error Definition ────────────────────────────────

#[repr(C)]
pub struct OmniError {
    pub code: u32,
    pub message: *const u8,
    pub message_len: usize,
}

// ─── Zero-Cost Monadic Result ─────────────────────────────
// Sesuai aturan OMNI: Monadic Error Handling

#[repr(C)]
pub enum OmniResult<T> {
    Ok(T),
    Err(OmniError),
}

// ─── Zero-Copy OmniBuffer ─────────────────────────────────
// Digunakan untuk komunikasi lintas bahasa tanpa copy memori

#[repr(C)]
pub struct OmniBuffer_Impl {
    pub ptr: *mut u8,
    pub len: usize,
    pub capacity: usize,
}

#[no_mangle]
pub unsafe extern "C" fn omni_buffer_alloc(size: usize) -> OmniResult<OmniBuffer_Impl> {
    let layout = match Layout::array::<u8>(size) {
        Ok(l) => l,
        Err(_) => return OmniResult::Err(OmniError {
            code: 100,
            message: b"Invalid layout size".as_ptr(),
            message_len: 19,
        }),
    };

    let ptr = alloc(layout);
    if ptr.is_null() {
        return OmniResult::Err(OmniError {
            code: 101,
            message: b"Memory allocation failed".as_ptr(),
            message_len: 24,
        });
    }

    // Zero initialization for safety
    ptr::write_bytes(ptr, 0, size);

    OmniResult::Ok(OmniBuffer_Impl {
        ptr,
        len: size,
        capacity: size,
    })
}

#[no_mangle]
pub unsafe extern "C" fn omni_buffer_free(buffer: *mut OmniBuffer_Impl) -> OmniResult<()> {
    if buffer.is_null() {
        return OmniResult::Err(OmniError {
            code: 102,
            message: b"Null pointer exception".as_ptr(),
            message_len: 22,
        });
    }

    let buf = &mut *buffer;
    if !buf.ptr.is_null() && buf.capacity > 0 {
        let layout = Layout::array::<u8>(buf.capacity).unwrap();
        dealloc(buf.ptr, layout);
        buf.ptr = ptr::null_mut();
        buf.len = 0;
        buf.capacity = 0;
    }

    OmniResult::Ok(())
}
