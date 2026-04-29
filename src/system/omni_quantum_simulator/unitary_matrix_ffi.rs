#[no_mangle]
pub extern "C" fn omni_apply_hadamard_gate(
    real_0: *mut f64,
    imag_0: *mut f64,
    real_1: *mut f64,
    imag_1: *mut f64,
    err_code: *mut i32,
) {
    if err_code.is_null() {
        return;
    }

    if real_0.is_null() || imag_0.is_null() || real_1.is_null() || imag_1.is_null() {
        unsafe { *err_code = -1 };
        return;
    }

    // Zero-mock hardware-level execution of Hadamard Unitary Matrix
    // Transforms basis states into superposition
    unsafe {
        use std::f64::consts::SQRT_2;
        let inv_sqrt2 = 1.0 / SQRT_2;

        let r0 = *real_0;
        let i0 = *imag_0;
        let r1 = *real_1;
        let i1 = *imag_1;

        // Matrix multiplication: [1/sqrt(2), 1/sqrt(2); 1/sqrt(2), -1/sqrt(2)] * [r0+i0; r1+i1]
        *real_0 = inv_sqrt2 * (r0 + r1);
        *imag_0 = inv_sqrt2 * (i0 + i1);
        
        *real_1 = inv_sqrt2 * (r0 - r1);
        *imag_1 = inv_sqrt2 * (i0 - i1);

        *err_code = 0;
    }
}
