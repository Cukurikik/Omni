use std::fs::File;
use std::os::raw::c_char;
use std::ffi::CStr;
// In zero-mock env we use pure Rust file reading to simulate mmap for safety

#[no_mangle]
pub extern "C" fn omni_mmap_dataset_chunk(
    file_path_ptr: *const c_char,
    offset: u64,
    size: u64,
    out_buffer: *mut u8,
    err_code: *mut i32,
) {
    if err_code.is_null() {
        return;
    }

    if file_path_ptr.is_null() || out_buffer.is_null() || size == 0 {
        unsafe { *err_code = -1 };
        return;
    }

    let c_str = unsafe { CStr::from_ptr(file_path_ptr) };
    let path = match c_str.to_str() {
        Ok(s) => s,
        Err(_) => {
            unsafe { *err_code = -2 };
            return;
        }
    };

    use std::io::{Read, Seek, SeekFrom};
    let mut file = match File::open(path) {
        Ok(f) => f,
        Err(_) => {
            unsafe { *err_code = -3 };
            return;
        }
    };

    if file.seek(SeekFrom::Start(offset)).is_err() {
        unsafe { *err_code = -4 };
        return;
    }

    // Unsafe slice from raw pointer for FFI buffer fill
    let buffer_slice = unsafe { std::slice::from_raw_parts_mut(out_buffer, size as usize) };
    
    match file.read_exact(buffer_slice) {
        Ok(_) => unsafe { *err_code = 0 },
        Err(_) => unsafe { *err_code = -5 },
    }
}
