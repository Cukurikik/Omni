use std::os::raw::{c_char, c_int};
use std::ffi::CStr;
use std::cmp::min;

#[repr(C)]
pub struct OmniResult {
    pub distance: c_int,
    pub status: c_int, // 0 = OK, 1 = Error
}

/// Computes the Levenshtein edit distance between two strings
#[no_mangle]
pub extern "C" fn omni_levenshtein_distance(
    s1_ptr: *const c_char,
    s2_ptr: *const c_char,
) -> OmniResult {
    if s1_ptr.is_null() || s2_ptr.is_null() {
        return OmniResult { distance: -1, status: 1 };
    }

    let s1 = unsafe {
        match CStr::from_ptr(s1_ptr).to_str() {
            Ok(s) => s,
            Err(_) => return OmniResult { distance: -1, status: 1 },
        }
    };

    let s2 = unsafe {
        match CStr::from_ptr(s2_ptr).to_str() {
            Ok(s) => s,
            Err(_) => return OmniResult { distance: -1, status: 1 },
        }
    };

    let len1 = s1.chars().count();
    let len2 = s2.chars().count();

    if len1 == 0 { return OmniResult { distance: len2 as c_int, status: 0 }; }
    if len2 == 0 { return OmniResult { distance: len1 as c_int, status: 0 }; }

    // Memory efficient 2-row approach
    let mut row_prev: Vec<usize> = (0..=len2).collect();
    let mut row_curr = vec![0; len2 + 1];

    for (i, c1) in s1.chars().enumerate() {
        row_curr[0] = i + 1;
        for (j, c2) in s2.chars().enumerate() {
            let cost = if c1 == c2 { 0 } else { 1 };
            row_curr[j + 1] = min(
                min(row_curr[j] + 1, row_prev[j + 1] + 1),
                row_prev[j] + cost,
            );
        }
        row_prev.copy_from_slice(&row_curr);
    }

    OmniResult {
        distance: row_curr[len2] as c_int,
        status: 0,
    }
}
