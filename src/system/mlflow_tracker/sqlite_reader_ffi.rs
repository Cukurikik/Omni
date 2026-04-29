use std::os::raw::c_char;
use std::ffi::CStr;
use std::fs::File;
use std::io::Read;

#[no_mangle]
pub extern "C" fn omni_read_sqlite_header(
    db_path_ptr: *const c_char,
    out_magic_buffer: *mut u8,
    err_code: *mut i32,
) {
    if err_code.is_null() {
        return;
    }

    if db_path_ptr.is_null() || out_magic_buffer.is_null() {
        unsafe { *err_code = -1 };
        return;
    }

    let c_str = unsafe { CStr::from_ptr(db_path_ptr) };
    let path = match c_str.to_str() {
        Ok(s) => s,
        Err(_) => {
            unsafe { *err_code = -2 };
            return;
        }
    };

    let mut file = match File::open(path) {
        Ok(f) => f,
        Err(_) => {
            unsafe { *err_code = -3 };
            return;
        }
    };

    // Read exactly 16 bytes (SQLite magic header "SQLite format 3\0")
    let buffer_slice = unsafe { std::slice::from_raw_parts_mut(out_magic_buffer, 16) };
    
    match file.read_exact(buffer_slice) {
        Ok(_) => unsafe { *err_code = 0 },
        Err(_) => unsafe { *err_code = -4 },
    }
}
