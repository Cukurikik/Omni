// omni_ffi_bridge.rs — Rust FFI Bridge to C++ Tracking Engine
// Layer: System / Rust
//
// Safe Rust wrapper for the TransCenter Multiple Object Tracking C++ ABI.
// Ensures zero-copy data transfer and memory safety across language boundaries.

#![allow(non_camel_case_types)]
#![allow(dead_code)]

use std::ffi::c_void;
use std::os::raw::{c_float, c_int};

/// Opaque pointer to the C++ OmniTracker instance
#[repr(C)]
pub struct COmniTracker {
    _private: [u8; 0],
}

#[repr(C)]
#[derive(Debug, Clone, Copy)]
pub struct CTrackBBox {
    pub id: c_int,
    pub x: c_float,
    pub y: c_float,
    pub w: c_float,
    pub h: c_float,
}

// C-API declared in the C++ layer
extern "C" {
    fn omni_tracker_new(width: c_int, height: c_int) -> *mut COmniTracker;
    fn omni_tracker_free(tracker: *mut COmniTracker);
    fn omni_tracker_update(
        tracker: *mut COmniTracker,
        centers_x: *const c_float,
        centers_y: *const c_float,
        sizes_w: *const c_float,
        sizes_h: *const c_float,
        count: c_int,
        out_boxes: *mut CTrackBBox,
        out_capacity: c_int,
    ) -> c_int;
}

/// Safe Rust Abstraction
pub struct OmniTracker {
    ptr: *mut COmniTracker,
}

impl OmniTracker {
    pub fn new(width: i32, height: i32) -> Result<Self, &'static str> {
        let ptr = unsafe { omni_tracker_new(width, height) };
        if ptr.is_null() {
            return Err("Failed to initialize C++ OmniTracker");
        }
        Ok(Self { ptr })
    }

    pub fn update(
        &mut self,
        centers_x: &[f32],
        centers_y: &[f32],
        sizes_w: &[f32],
        sizes_h: &[f32],
    ) -> Vec<CTrackBBox> {
        let count = centers_x.len() as i32;
        assert_eq!(count as usize, centers_y.len());
        assert_eq!(count as usize, sizes_w.len());
        assert_eq!(count as usize, sizes_h.len());

        let out_capacity = count * 2; // Allocate buffer
        let mut out_buffer: Vec<CTrackBBox> = Vec::with_capacity(out_capacity as usize);

        let returned_count = unsafe {
            omni_tracker_update(
                self.ptr,
                centers_x.as_ptr(),
                centers_y.as_ptr(),
                sizes_w.as_ptr(),
                sizes_h.as_ptr(),
                count,
                out_buffer.as_mut_ptr(),
                out_capacity,
            )
        };

        unsafe {
            out_buffer.set_len(returned_count as usize);
        }

        out_buffer
    }
}

impl Drop for OmniTracker {
    fn drop(&mut self) {
        if !self.ptr.is_null() {
            unsafe {
                omni_tracker_free(self.ptr);
            }
            self.ptr = std::ptr::null_mut();
        }
    }
}
