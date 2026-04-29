#[no_mangle]
pub extern "C" fn omni_raft_serialize_append_entries(
    term: u64,
    leader_id: u64,
    prev_log_index: u64,
    prev_log_term: u64,
    leader_commit: u64,
    out_buffer: *mut u8,
    out_capacity: usize,
    err_code: *mut i32,
) {
    if err_code.is_null() {
        return;
    }

    if out_buffer.is_null() || out_capacity < 40 {
        unsafe { *err_code = -1 }; // Need exactly 40 bytes for the header fields
        return;
    }

    // Zero-mock deterministic fast binary serialization of Raft AppendEntries RPC header
    unsafe {
        let slice = std::slice::from_raw_parts_mut(out_buffer, 40);
        
        // Fast manual copy for zero-cost abstraction FFI
        slice[0..8].copy_from_slice(&term.to_be_bytes());
        slice[8..16].copy_from_slice(&leader_id.to_be_bytes());
        slice[16..24].copy_from_slice(&prev_log_index.to_be_bytes());
        slice[24..32].copy_from_slice(&prev_log_term.to_be_bytes());
        slice[32..40].copy_from_slice(&leader_commit.to_be_bytes());

        *err_code = 0;
    }
}
