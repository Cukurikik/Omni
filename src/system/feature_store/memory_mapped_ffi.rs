#[no_mangle]
pub extern "C" fn omni_fast_mmap_scan(
    mmap_ptr: *const u8,
    mmap_size: usize,
    target_entity_id: i32,
    out_value: *mut f64,
    err_code: *mut i32,
) {
    if err_code.is_null() {
        return;
    }

    if mmap_ptr.is_null() || out_value.is_null() {
        unsafe { *err_code = -1 };
        return;
    }

    // Deterministic binary struct layout simulation for fast feature store retrieval
    // Struct layout: [EntityID (4 bytes)] [Timestamp (8 bytes)] [Value (8 bytes)] = 20 bytes total
    let record_size = 20;
    
    if mmap_size % record_size != 0 {
        unsafe { *err_code = -2 }; // Misaligned map
        return;
    }

    let num_records = mmap_size / record_size;
    let data = unsafe { std::slice::from_raw_parts(mmap_ptr, mmap_size) };

    // Linear scan for simplicity, optimized mathematically
    // In production, this would be a binary search if sorted by entity_id
    
    let mut found = false;
    let mut latest_ts = 0u64;
    let mut best_val = 0.0;

    for i in 0..num_records {
        let offset = i * record_size;
        
        let entity_id = i32::from_le_bytes([
            data[offset], data[offset+1], data[offset+2], data[offset+3]
        ]);

        if entity_id == target_entity_id {
            let ts = u64::from_le_bytes([
                data[offset+4], data[offset+5], data[offset+6], data[offset+7],
                data[offset+8], data[offset+9], data[offset+10], data[offset+11]
            ]);

            if ts > latest_ts {
                latest_ts = ts;
                best_val = f64::from_le_bytes([
                    data[offset+12], data[offset+13], data[offset+14], data[offset+15],
                    data[offset+16], data[offset+17], data[offset+18], data[offset+19]
                ]);
                found = true;
            }
        }
    }

    if found {
        unsafe { 
            *out_value = best_val;
            *err_code = 0; 
        };
    } else {
        unsafe { *err_code = 1 }; // Not found
    }
}
