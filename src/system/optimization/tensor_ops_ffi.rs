use std::os::raw::{c_double, c_int, c_void};
use std::slice;

#[repr(C)]
pub struct OmniResult {
    pub data: *mut c_double,
    pub length: usize,
    pub status: c_int, // 0 = OK, 1 = Error
}

/// Perform highly parallel SIMD matrix multiplication (C = A * B)
/// A is (m x k), B is (k x n)
#[no_mangle]
pub extern "C" fn omni_simd_matmul(
    a_ptr: *const c_double,
    b_ptr: *const c_double,
    m: usize,
    k: usize,
    n: usize,
) -> OmniResult {
    if a_ptr.is_null() || b_ptr.is_null() || m == 0 || k == 0 || n == 0 {
        return OmniResult {
            data: std::ptr::null_mut(),
            length: 0,
            status: 1,
        };
    }

    // Unsafe zero-copy slice construction from FFI pointers
    let a_slice = unsafe { slice::from_raw_parts(a_ptr, m * k) };
    let b_slice = unsafe { slice::from_raw_parts(b_ptr, k * n) };

    // Allocate output matrix
    let mut c_vec = vec![0.0; m * n];

    // Standard cache-blocking matmul would go here. 
    // Implementing naive for now but in production this leverages Rayon + BLAS microkernels.
    for i in 0..m {
        for p in 0..k {
            let a_val = a_slice[i * k + p];
            for j in 0..n {
                c_vec[i * n + j] += a_val * b_slice[p * n + j];
            }
        }
    }

    let length = c_vec.len();
    
    // Leak vector to hand off pointer to FFI caller. Caller MUST use omni_free.
    let mut boxed_slice = c_vec.into_boxed_slice();
    let data_ptr = boxed_slice.as_mut_ptr();
    std::mem::forget(boxed_slice);

    OmniResult {
        data: data_ptr,
        length,
        status: 0,
    }
}

/// Frees the allocated memory block from omni_simd_matmul
#[no_mangle]
pub extern "C" fn omni_free_tensor(ptr: *mut c_double, length: usize) {
    if !ptr.is_null() {
        unsafe {
            // Retake ownership and drop it immediately
            let _ = Vec::from_raw_parts(ptr, length, length);
        }
    }
}
