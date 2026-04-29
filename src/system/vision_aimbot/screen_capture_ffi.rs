#[no_mangle]
pub extern "C" fn omni_process_frame_buffer(
    frame_pixels: *const u8,
    width: i32,
    height: i32,
    channels: i32, // e.g., 3 for RGB
    threshold: u8,
    out_mask: *mut u8,
    err_code: *mut i32,
) {
    if err_code.is_null() {
        return;
    }

    if frame_pixels.is_null() || out_mask.is_null() || width <= 0 || height <= 0 || channels <= 0 {
        unsafe { *err_code = -1 };
        return;
    }

    let total_pixels = (width * height) as usize;
    
    let input = unsafe { std::slice::from_raw_parts(frame_pixels, total_pixels * (channels as usize)) };
    let output = unsafe { std::slice::from_raw_parts_mut(out_mask, total_pixels) };

    // High-speed deterministic color thresholding mapping (e.g. searching for enemy outline color)
    // Red-dominant isolation mathematical logic
    for i in 0..total_pixels {
        let r = input[i * (channels as usize)];
        let g = input[i * (channels as usize) + 1];
        let b = input[i * (channels as usize) + 2];

        // Strict deterministic rule: R must be significantly higher than G and B, and above threshold
        if r > threshold && r > (g.saturating_add(20)) && r > (b.saturating_add(20)) {
            output[i] = 255; // Hit mask
        } else {
            output[i] = 0;   // Miss
        }
    }

    unsafe { *err_code = 0 };
}
