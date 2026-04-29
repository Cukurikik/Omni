// OMNI System Layer - CoE Tensor Ops
pub enum CoETensorError {
    DimensionMismatch,
    EmptyTensor,
}

pub struct Tensor {
    pub data: Vec<f32>,
    pub shape: Vec<usize>,
}

impl Tensor {
    pub fn self_evaluate_variance(&self) -> Result<f32, CoETensorError> {
        if self.data.is_empty() {
            return Err(CoETensorError::EmptyTensor);
        }

        let mean: f32 = self.data.iter().sum::<f32>() / self.data.len() as f32;
        let var: f32 = self.data.iter().map(|&x| (x - mean).powi(2)).sum::<f32>() / self.data.len() as f32;

        Ok(var)
    }
}
