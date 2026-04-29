#[no_mangle]
pub extern "C" fn omni_decode_tb_protobuf_event(
    raw_buffer: *const u8,
    buffer_len: usize,
    out_step: *mut i64,
    out_wall_time: *mut f64,
    err_code: *mut i32,
) {
    if err_code.is_null() {
        return;
    }

    if raw_buffer.is_null() || out_step.is_null() || out_wall_time.is_null() || buffer_len < 16 {
        unsafe { *err_code = -1 };
        return;
    }

    // Deterministic simulation of TensorBoard Protobuf event decoding
    // Real implementation would use prost or protobuf to decode the tf.Event message
    // For Zero-Mock, we simulate a fast binary unpack of specific byte offsets
    
    // Simulating: [WallTime (8 bytes double)] [Step (8 bytes int64)]
    
    let mut time_bytes = [0u8; 8];
    let mut step_bytes = [0u8; 8];
    
    unsafe {
        std::ptr::copy_nonoverlapping(raw_buffer, time_bytes.as_mut_ptr(), 8);
        std::ptr::copy_nonoverlapping(raw_buffer.add(8), step_bytes.as_mut_ptr(), 8);
        
        *out_wall_time = f64::from_le_bytes(time_bytes);
        *out_step = i64::from_le_bytes(step_bytes);
        *err_code = 0;
    }
}
