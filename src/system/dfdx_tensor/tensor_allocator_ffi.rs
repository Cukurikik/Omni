use std::alloc::{alloc_zeroed, dealloc, Layout};
use std::ptr;

#[no_mangle]
pub extern "C" fn omni_allocate_tensor_f32(
    num_elements: usize,
    out_ptr: *mut *mut f32,
    err_code: *mut i32,
) {
    if err_code.is_null() {
        return;
    }

    if out_ptr.is_null() || num_elements == 0 {
        unsafe { *err_code = -1 };
        return;
    }

    // Mathematical memory layout requirement: Float32 = 4 bytes, aligned to 4 bytes
    // Using raw system allocator for zero-overhead tensor creation like dfdx
    let layout = match Layout::array::<f32>(num_elements) {
        Ok(l) => l,
        Err(_) => {
            unsafe { *err_code = -2 }; // Memory size overflow mathematically
            return;
        }
    };

    unsafe {
        let ptr = alloc_zeroed(layout) as *mut f32;
        if ptr.is_null() {
            *err_code = -3; // OOM
            return;
        }
        *out_ptr = ptr;
        *err_code = 0;
    }
}

#[no_mangle]
pub extern "C" fn omni_free_tensor_f32(
    ptr: *mut f32,
    num_elements: usize,
) {
    if ptr.is_null() || num_elements == 0 {
        return;
    }

    if let Ok(layout) = Layout::array::<f32>(num_elements) {
        unsafe {
            dealloc(ptr as *mut u8, layout);
        }
    }
}
