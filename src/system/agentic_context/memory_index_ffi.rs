#[no_mangle]
pub extern "C" fn omni_update_memory_index(
    current_state: *const f64,
    new_experience: *const f64,
    dim: i32,
    learning_rate: f64,
    out_state: *mut f64,
    err_code: *mut i32,
) {
    if err_code.is_null() {
        return;
    }

    if current_state.is_null() || new_experience.is_null() || out_state.is_null() || dim <= 0 {
        unsafe { *err_code = -1 };
        return;
    }

    let state_slice = unsafe { std::slice::from_raw_parts(current_state, dim as usize) };
    let exp_slice = unsafe { std::slice::from_raw_parts(new_experience, dim as usize) };
    let out_slice = unsafe { std::slice::from_raw_parts_mut(out_state, dim as usize) };

    // Deterministic mathematical update of context memory (Exponential Moving Average representation)
    for i in 0..(dim as usize) {
        out_slice[i] = (1.0 - learning_rate) * state_slice[i] + (learning_rate * exp_slice[i]);
    }

    unsafe { *err_code = 0 };
}
