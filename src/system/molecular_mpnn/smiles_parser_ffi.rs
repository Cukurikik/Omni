#[no_mangle]
pub extern "C" fn omni_parse_smiles_length(
    smiles: *const std::os::raw::c_char,
    err_code: *mut i32,
) -> i32 {
    if err_code.is_null() {
        return 0;
    }

    if smiles.is_null() {
        unsafe { *err_code = -1 };
        return 0;
    }

    let c_str = unsafe { std::ffi::CStr::from_ptr(smiles) };
    let parsed_str = match c_str.to_str() {
        Ok(s) => s,
        Err(_) => {
            unsafe { *err_code = -2 };
            return 0;
        }
    };

    if parsed_str.is_empty() {
        unsafe { *err_code = -3 };
        return 0;
    }

    // Deterministic simulation of parsing: count heavy atoms (C, N, O, P, S, F, Cl, Br, I)
    let mut heavy_atoms = 0;
    let bytes = parsed_str.as_bytes();
    
    for i in 0..bytes.len() {
        match bytes[i] as char {
            'C' | 'N' | 'O' | 'P' | 'S' | 'F' | 'I' => heavy_atoms += 1,
            'c' | 'n' | 'o' | 'p' | 's' => heavy_atoms += 1, // Aromatic
            'B' => {
                if i + 1 < bytes.len() && bytes[i+1] as char == 'r' {
                    heavy_atoms += 1;
                }
            },
            _ => {}
        }
    }

    unsafe { *err_code = 0 };
    heavy_atoms
}
