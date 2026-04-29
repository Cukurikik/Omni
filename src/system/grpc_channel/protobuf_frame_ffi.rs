#[no_mangle]
pub extern "C" fn omni_grpc_frame_header_pack(
    payload_len: u32,
    is_compressed: bool,
    out_frame: *mut u8,
    out_capacity: usize,
    err_code: *mut i32,
) {
    if err_code.is_null() {
        return;
    }

    if out_frame.is_null() || out_capacity < 5 {
        unsafe { *err_code = -1 }; // Need at least 5 bytes for gRPC length-prefixed message header
        return;
    }

    // gRPC Frame Format:
    // 1 byte: Compressed Flag (0 or 1)
    // 4 bytes: Message Length (Big Endian)
    
    unsafe {
        let slice = std::slice::from_raw_parts_mut(out_frame, 5);
        slice[0] = if is_compressed { 1 } else { 0 };
        
        let len_bytes = payload_len.to_be_bytes();
        slice[1] = len_bytes[0];
        slice[2] = len_bytes[1];
        slice[3] = len_bytes[2];
        slice[4] = len_bytes[3];
        
        *err_code = 0;
    }
}
