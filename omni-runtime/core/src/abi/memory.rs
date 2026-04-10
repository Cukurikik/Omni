#![allow(clippy::missing_safety_doc)]

use std::alloc::{alloc, dealloc, Layout};
use std::slice;

/// OMNI-ABI: OMNI Buffer Structure (C-Compatible)
/// Represents a raw pointer and its size, ensuring zero-copy when passed
/// between JS (SharedArrayBuffer), C++ (std::span), Golang (C.void), and Rust.
#[repr(C)]
pub struct OmniBuffer {
    pub data: *mut u8,
    pub length: usize,
    pub capacity: usize,
}

/// Allocates an OmniBuffer of the exact size on the Master Allocator (Rust)
#[no_mangle]
pub unsafe extern "C" fn omni_allocate(size: usize) -> *mut OmniBuffer {
    let layout = Layout::array::<u8>(size).unwrap();
    let data = alloc(layout);
    
    // Allocate the wrapper struct itself on the heap so it can be passed around
    let wrapper_layout = Layout::new::<OmniBuffer>();
    let wrapper_ptr = alloc(wrapper_layout) as *mut OmniBuffer;
    
    *wrapper_ptr = OmniBuffer {
        data,
        length: size,
        capacity: size,
    };
    
    wrapper_ptr
}

/// Frees an OmniBuffer back to the system memory
#[no_mangle]
pub unsafe extern "C" fn omni_free(buffer: *mut OmniBuffer) {
    if buffer.is_null() { return; }
    
    let buf = &*buffer;
    let layout = Layout::array::<u8>(buf.capacity).unwrap();
    dealloc(buf.data, layout);
    
    let wrapper_layout = Layout::new::<OmniBuffer>();
    dealloc(buffer as *mut u8, wrapper_layout);
}

/// Test Mock: Applies a dummy "encryption/mutation" over the zero-copy buffer
/// Shows that Rust can mutate memory held by Python/JS purely via pointer.
#[no_mangle]
pub unsafe extern "C" fn omni_mutate_matrix(buffer: *mut OmniBuffer) {
    if buffer.is_null() { return; }
    let buf = &*buffer;
    
    // Menganimasikan mutasi zero-copy. Array Rust mem-wrap address dari memori C.
    let slice = slice::from_raw_parts_mut(buf.data, buf.length);
    for byte in slice.iter_mut() {
        *byte = byte.wrapping_add(42); // Dummy operation
    }
}
