#[no_mangle]
pub extern "C" fn omni_sparse_matrix_multiply(
    adj_matrix_values: *const f32,
    adj_matrix_col_idx: *const i32,
    adj_matrix_row_ptr: *const i32,
    node_features: *const f32,
    num_nodes: i32,
    feature_dim: i32,
    out_features: *mut f32,
    err_code: *mut i32,
) {
    if err_code.is_null() {
        return;
    }

    if adj_matrix_values.is_null() || node_features.is_null() || out_features.is_null() {
        unsafe { *err_code = -1 };
        return;
    }

    // Zero-mock deterministic SpMM (Sparse Matrix-Dense Matrix Multiplication)
    // Core math for Graph Convolutional Networks (GCN)
    unsafe {
        for i in 0..num_nodes {
            let row_start = adj_matrix_row_ptr[i as usize] as usize;
            let row_end = adj_matrix_row_ptr[(i + 1) as usize] as usize;

            for f in 0..feature_dim {
                let mut sum = 0.0;
                for j in row_start..row_end {
                    let col = adj_matrix_col_idx[j] as usize;
                    let val = adj_matrix_values[j];
                    sum += val * node_features[col * (feature_dim as usize) + (f as usize)];
                }
                out_features[(i * feature_dim + f) as usize] = sum;
            }
        }
        *err_code = 0;
    }
}
