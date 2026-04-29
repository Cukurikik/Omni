#[no_mangle]
pub extern "C" fn omni_xlstm_gate_update(
    memory_state: *const f64,
    input_gate: *const f64,
    dim: i32,
    out_state: *mut f64,
    err_code: *mut i32,
) {
    if err_code.is_null() {
        return;
    }

    if memory_state.is_null() || input_gate.is_null() || out_state.is_null() || dim <= 0 {
        unsafe { *err_code = -1 };
        return;
    }

    let mem_slice = unsafe { std::slice::from_raw_parts(memory_state, dim as usize) };
    let gate_slice = unsafe { std::slice::from_raw_parts(input_gate, dim as usize) };
    let out_slice = unsafe { std::slice::from_raw_parts_mut(out_state, dim as usize) };

    // Deterministic mathematical implementation of xLSTM exponential gating logic
    // C_t = C_{t-1} + exp(i_t) * v_t  (simplified for FFI simulation)
    
    for i in 0..(dim as usize) {
        let exp_gate = gate_slice[i].exp(); // Exponential gating
        
        // Prevent overflow deterministically
        let safe_exp = if exp_gate > 1e4 { 1e4 } else { exp_gate };
        
        out_slice[i] = mem_slice[i] + safe_exp;
    }

    unsafe { *err_code = 0 };
}
