#[no_mangle]
pub extern "C" fn omni_parse_prompt_template(
    template_str: *const u8,
    template_len: usize,
    out_vars_buffer: *mut u8,
    max_out_len: usize,
    bytes_written: *mut usize,
    err_code: *mut i32,
) {
    if err_code.is_null() {
        return;
    }

    if template_str.is_null() || out_vars_buffer.is_null() || bytes_written.is_null() {
        unsafe { *err_code = -1 };
        return;
    }

    let input = unsafe { std::slice::from_raw_parts(template_str, template_len) };
    let out = unsafe { std::slice::from_raw_parts_mut(out_vars_buffer, max_out_len) };

    let mut in_bracket = false;
    let mut current_var_start = 0;
    let mut write_pos = 0;

    // Fast deterministic parsing of {variables} in string templates
    for i in 0..template_len {
        let c = input[i];
        if c == b'{' {
            in_bracket = true;
            current_var_start = i + 1;
        } else if c == b'}' && in_bracket {
            in_bracket = false;
            let var_len = i - current_var_start;
            
            if write_pos + var_len + 1 > max_out_len {
                unsafe { *err_code = -2 }; // Buffer overflow
                return;
            }

            // Copy variable name to output buffer, separated by commas
            for j in 0..var_len {
                out[write_pos] = input[current_var_start + j];
                write_pos += 1;
            }
            out[write_pos] = b',';
            write_pos += 1;
        }
    }

    if write_pos > 0 {
        write_pos -= 1; // Remove trailing comma
    }

    unsafe { 
        *bytes_written = write_pos;
        *err_code = 0;
    }
}
