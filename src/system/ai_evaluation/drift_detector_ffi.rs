#[no_mangle]
pub extern "C" fn omni_detect_drift(
    data: *const f64,
    length: i32,
    err_code: *mut i32,
) -> f64 {
    if err_code.is_null() {
        return 0.0;
    }

    if data.is_null() || length <= 1 {
        unsafe { *err_code = -1 };
        return 0.0;
    }

    // Deterministic mathematical drift calculation (Simplified Variance/Slope over time)
    let slice = unsafe { std::slice::from_raw_parts(data, length as usize) };
    
    let mut sum_diff = 0.0;
    for i in 1..slice.len() {
        let diff = slice[i] - slice[i-1];
        // Calculate cumulative squared difference
        sum_diff += diff * diff;
    }
    
    // Normalize drift score
    let drift_score = sum_diff / (slice.len() as f64);

    unsafe { *err_code = 0 };
    drift_score
}
