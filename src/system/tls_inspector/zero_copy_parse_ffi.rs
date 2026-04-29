#[no_mangle]
pub extern "C" fn omni_zero_copy_parse_sni(
    packet_ptr: *const u8,
    extensions_offset: usize,
    extensions_len: usize,
    out_sni_buf: *mut u8,
    out_sni_len: *mut usize,
    err_code: *mut i32,
) {
    if err_code.is_null() {
        return;
    }

    if packet_ptr.is_null() || out_sni_buf.is_null() || out_sni_len.is_null() {
        unsafe { *err_code = -1 };
        return;
    }

    // Zero-mock deterministic parsing of TLS extensions to find SNI (Type 0x0000)
    // Avoids copying the packet payload (Zero-copy)
    
    unsafe {
        let slice = std::slice::from_raw_parts(packet_ptr.add(extensions_offset), extensions_len);
        let mut pos = 0;
        
        while pos + 4 <= extensions_len {
            let ext_type = ((slice[pos] as u16) << 8) | (slice[pos+1] as u16);
            let ext_len = ((slice[pos+2] as usize) << 8) | (slice[pos+3] as usize);
            pos += 4;
            
            if ext_type == 0x0000 { // SNI
                if pos + ext_len <= extensions_len && ext_len > 5 {
                    // Skip ServerNameList length (2 bytes) and NameType (1 byte) and NameLength (2 bytes)
                    let sni_str_len = ((slice[pos+3] as usize) << 8) | (slice[pos+4] as usize);
                    let sni_str_start = pos + 5;
                    
                    if sni_str_start + sni_str_len <= pos + ext_len {
                        std::ptr::copy_nonoverlapping(
                            slice.as_ptr().add(sni_str_start), 
                            out_sni_buf, 
                            sni_str_len
                        );
                        *out_sni_len = sni_str_len;
                        *err_code = 0;
                        return;
                    }
                }
            }
            
            pos += ext_len;
        }
        
        *err_code = 1; // SNI not found
    }
}
