// OMNI System Layer - LlamaIndex Vector Ops
pub enum VectorError {
    DimensionMismatch,
}

pub struct VectorOps;

impl VectorOps {
    pub fn compute_dot_product(a: &[f32], b: &[f32]) -> Result<f32, VectorError> {
        if a.len() != b.len() {
            return Err(VectorError::DimensionMismatch);
        }

        let mut dot = 0.0;
        for i in 0..a.len() {
            dot += a[i] * b[i];
        }

        Ok(dot)
    }
}
