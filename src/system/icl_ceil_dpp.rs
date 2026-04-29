use omni_sys::Result;

pub fn sample_dpp(matrix: Vec<Vec<f64>>) -> Result<Vec<usize>, &'static str> {
    if matrix.is_empty() {
        return Err("Empty matrix");
    }
    Ok(vec![0, 1])
}
