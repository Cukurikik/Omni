// @omni-domain System Layer (Data SIMD)
// @omni-source various/data-prep
// @omni-description Data Prep SIMD mimicking vectorized data transforms in Rust.
// @omni-requirement zero-mock, monadic-error
pub enum SimdError { EmptyData, InvalidRange }
pub type OmniResult<T> = Result<T, SimdError>;

pub fn vectorized_normalize(data: &mut [f64]) -> OmniResult<()> {
    if data.is_empty() { return Err(SimdError::EmptyData); }
    let min = data.iter().cloned().fold(f64::INFINITY, f64::min);
    let max = data.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    if (max - min).abs() < 1e-15 { return Err(SimdError::InvalidRange); }
    let range = max - min;
    for val in data.iter_mut() { *val = (*val - min) / range; }
    Ok(())
}

pub fn vectorized_dot_product(a: &[f64], b: &[f64]) -> OmniResult<f64> {
    if a.is_empty() || b.is_empty() { return Err(SimdError::EmptyData); }
    if a.len() != b.len() { return Err(SimdError::InvalidRange); }
    Ok(a.iter().zip(b.iter()).map(|(x, y)| x * y).sum())
}

pub fn vectorized_scale(data: &mut [f64], factor: f64) -> OmniResult<()> {
    if data.is_empty() { return Err(SimdError::EmptyData); }
    for val in data.iter_mut() { *val *= factor; }
    Ok(())
}
