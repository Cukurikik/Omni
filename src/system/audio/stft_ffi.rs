use std::os::raw::{c_double, c_int};
use std::slice;
use std::f64::consts::PI;

#[repr(C)]
pub struct OmniComplex {
    pub real: f64,
    pub imag: f64,
}

#[repr(C)]
pub struct OmniResult {
    pub data: *mut OmniComplex,
    pub rows: usize,
    pub cols: usize,
    pub status: c_int,
}

// Minimal struct for STFT (Short-Time Fourier Transform)
#[no_mangle]
pub extern "C" fn omni_stft(
    signal_ptr: *const c_double,
    length: usize,
    window_size: usize,
    hop_size: usize,
) -> OmniResult {
    if signal_ptr.is_null() || length == 0 || window_size == 0 || hop_size == 0 {
        return OmniResult {
            data: std::ptr::null_mut(),
            rows: 0, cols: 0, status: 1
        };
    }

    let signal = unsafe { slice::from_raw_parts(signal_ptr, length) };
    
    let num_frames = 1 + (length.saturating_sub(window_size)) / hop_size;
    let freq_bins = window_size / 2 + 1;
    
    let mut stft_matrix = vec![OmniComplex { real: 0.0, imag: 0.0 }; num_frames * freq_bins];

    // Hann Window precompute
    let mut window = vec![0.0; window_size];
    for i in 0..window_size {
        window[i] = 0.5 * (1.0 - f64::cos(2.0 * PI * (i as f64) / (window_size as f64 - 1.0)));
    }

    // Structural Discrete Fourier Transform implementation (replace with RustFFT in true prod)
    for t in 0..num_frames {
        let start_idx = t * hop_size;
        for k in 0..freq_bins {
            let mut real_sum = 0.0;
            let mut imag_sum = 0.0;
            for n in 0..window_size {
                if start_idx + n < length {
                    let val = signal[start_idx + n] * window[n];
                    let angle = -2.0 * PI * (k as f64) * (n as f64) / (window_size as f64);
                    real_sum += val * f64::cos(angle);
                    imag_sum += val * f64::sin(angle);
                }
            }
            stft_matrix[t * freq_bins + k] = OmniComplex { real: real_sum, imag: imag_sum };
        }
    }

    let mut boxed_slice = stft_matrix.into_boxed_slice();
    let data_ptr = boxed_slice.as_mut_ptr();
    std::mem::forget(boxed_slice);

    OmniResult {
        data: data_ptr,
        rows: num_frames,
        cols: freq_bins,
        status: 0
    }
}

#[no_mangle]
pub extern "C" fn omni_free_stft(ptr: *mut OmniComplex, rows: usize, cols: usize) {
    if !ptr.is_null() {
        unsafe {
            let _ = Vec::from_raw_parts(ptr, rows * cols, rows * cols);
        }
    }
}
