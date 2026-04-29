#[no_mangle]
pub extern "C" fn omni_step_physics(
    pos_x: f64,
    velocity_x: f64,
    force: f64,
    mass: f64,
    dt: f64,
    out_new_pos: *mut f64,
    out_new_vel: *mut f64,
    err_code: *mut i32,
) {
    if err_code.is_null() {
        return;
    }

    if out_new_pos.is_null() || out_new_vel.is_null() || mass <= 0.0 || dt <= 0.0 {
        unsafe { *err_code = -1 };
        return;
    }

    // Simple deterministic 1D Euler integration for RL physics engine
    let acceleration = force / mass;
    let new_velocity = velocity_x + (acceleration * dt);
    let new_position = pos_x + (new_velocity * dt);

    unsafe {
        *out_new_pos = new_position;
        *out_new_vel = new_velocity;
        *err_code = 0;
    }
}
