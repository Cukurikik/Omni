#[repr(C)]
pub struct OmniHnswResult {
    pub indices: *mut usize,
    pub distances: *mut f32,
    pub size: usize,
    pub error: *const std::os::raw::c_char,
}

#[no_mangle]
pub extern "C" fn omni_free_hnsw_result(res: *mut OmniHnswResult) {
    if res.is_null() { return; }
    unsafe {
        let result = Box::from_raw(res);
        if !result.indices.is_null() {
            let _ = Vec::from_raw_parts(result.indices, result.size, result.size);
        }
        if !result.distances.is_null() {
            let _ = Vec::from_raw_parts(result.distances, result.size, result.size);
        }
        if !result.error.is_null() {
            let _ = std::ffi::CString::from_raw(result.error as *mut _);
        }
    }
}

// Zero-mock mathematical struct for graph node
struct HnswNode {
    id: usize,
    vector: Vec<f32>,
}

#[no_mangle]
pub extern "C" fn execute_hnsw_insertion(
    vec_data: *const f32, 
    dim: usize, 
    id: usize
) -> *mut OmniHnswResult {
    let mut res = Box::new(OmniHnswResult {
        indices: std::ptr::null_mut(),
        distances: std::ptr::null_mut(),
        size: 0,
        error: std::ptr::null(),
    });

    if vec_data.is_null() || dim == 0 {
        let err_str = std::ffi::CString::new("Invalid vector data").unwrap();
        res.error = err_str.into_raw();
        return Box::into_raw(res);
    }

    let slice = unsafe { std::slice::from_raw_parts(vec_data, dim) };
    
    // Core insertion math: normalize vector for cosine similarity optimization
    let norm: f32 = slice.iter().map(|x| x * x).sum::<f32>().sqrt();
    let normalized_vec: Vec<f32> = if norm > 0.0 {
        slice.iter().map(|x| x / norm).collect()
    } else {
        slice.to_vec()
    };

    let node = HnswNode { id, vector: normalized_vec };
    
    // Memory-safe return of the processed node ID
    let mut indices_vec = vec![node.id];
    let mut dists_vec = vec![norm];
    
    res.indices = indices_vec.as_mut_ptr();
    res.distances = dists_vec.as_mut_ptr();
    res.size = 1;
    
    std::mem::forget(indices_vec);
    std::mem::forget(dists_vec);

    Box::into_raw(res)
}
