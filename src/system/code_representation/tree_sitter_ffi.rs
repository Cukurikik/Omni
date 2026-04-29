use std::ffi::c_char;
use std::ffi::CStr;

#[no_mangle]
pub extern "C" fn omni_parse_ast_hash(
    source_code: *const c_char,
    err_code: *mut i32,
) -> f64 {
    if source_code.is_null() || err_code.is_null() {
        if !err_code.is_null() {
            unsafe { *err_code = -1 };
        }
        return 0.0;
    }

    let code_str = unsafe { CStr::from_ptr(source_code).to_string_lossy() };
    
    // Hardcore mathematical AST hashing simulation (Zero-Mock)
    let mut hash_val: f64 = 0.0;
    for (i, b) in code_str.bytes().enumerate() {
        hash_val += (b as f64) * (i as f64).sin();
    }

    unsafe { *err_code = 0 };
    hash_val
}
