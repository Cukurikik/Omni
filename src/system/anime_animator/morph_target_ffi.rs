#[no_mangle]
pub extern "C" fn omni_apply_affine_transform(
    base_points: *const f64,
    num_points: i32,
    scale: f64,
    rotation: f64,
    tx: f64,
    ty: f64,
    out_points: *mut f64,
    err_code: *mut i32,
) {
    if err_code.is_null() {
        return;
    }

    if base_points.is_null() || out_points.is_null() || num_points <= 0 {
        unsafe { *err_code = -1 };
        return;
    }

    let input = unsafe { std::slice::from_raw_parts(base_points, (num_points * 2) as usize) };
    let output = unsafe { std::slice::from_raw_parts_mut(out_points, (num_points * 2) as usize) };

    let cos_r = rotation.cos();
    let sin_r = rotation.sin();

    // Deterministic mathematical Affine Transformation 
    // [ x' ]   [ s*cos(r)  -s*sin(r) ] [ x ]   [ tx ]
    // [ y' ] = [ s*sin(r)   s*cos(r) ] [ y ] + [ ty ]

    for i in 0..(num_points as usize) {
        let x = input[i * 2];
        let y = input[i * 2 + 1];

        // Rotation & Scaling
        let rx = scale * (x * cos_r - y * sin_r);
        let ry = scale * (x * sin_r + y * cos_r);

        // Translation
        output[i * 2] = rx + tx;
        output[i * 2 + 1] = ry + ty;
    }

    unsafe { *err_code = 0 };
}
