use std::fs::OpenOptions;
use std::io::Write;
use std::ffi::CStr;
use std::os::raw::c_char;

#[no_mangle]
pub extern "C" fn omni_append_journal_entry(
    db_path_ptr: *const c_char,
    trial_id: i32,
    state_code: i32,
    value: f64,
    err_code: *mut i32,
) {
    if err_code.is_null() {
        return;
    }

    if db_path_ptr.is_null() {
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

    // Fast append-only journal file imitating SQLite WAL logic for Zero-Mock
    let mut file = match OpenOptions::new().create(true).append(true).open(path) {
        Ok(f) => f,
        Err(_) => {
            unsafe { *err_code = -3 };
            return;
        }
    };

    // Deterministic binary serialization layout
    let mut buffer = [0u8; 16];
    buffer[0..4].copy_from_slice(&trial_id.to_le_bytes());
    buffer[4..8].copy_from_slice(&state_code.to_le_bytes());
    buffer[8..16].copy_from_slice(&value.to_le_bytes());

    match file.write_all(&buffer) {
        Ok(_) => unsafe { *err_code = 0 },
        Err(_) => unsafe { *err_code = -4 },
    }
}
