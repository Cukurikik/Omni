#[no_mangle]
pub extern "C" fn omni_audio_apply_lowpass_filter(
    audio_samples: *mut f32,
    num_samples: i32,
    cutoff_freq: f32,
    sample_rate: f32,
    err_code: *mut i32,
) {
    if err_code.is_null() {
        return;
    }

    if audio_samples.is_null() || num_samples <= 0 || cutoff_freq <= 0.0 || sample_rate <= 0.0 {
        unsafe { *err_code = -1 };
        return;
    }

    // Zero-mock deterministic single-pole lowpass filter for DSP post-processing
    unsafe {
        use std::f32::consts::PI;
        
        let rc = 1.0 / (cutoff_freq * 2.0 * PI);
        let dt = 1.0 / sample_rate;
        let alpha = dt / (rc + dt);
        
        let mut prev_y = audio_samples[0];
        
        for i in 1..num_samples {
            let x = audio_samples[i as usize];
            let y = prev_y + alpha * (x - prev_y);
            audio_samples[i as usize] = y;
            prev_y = y;
        }
        
        *err_code = 0;
    }
}
