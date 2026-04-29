use omni_sys::Result;

pub struct RecLMTensor {
    data: Vec<f64>,
}

impl RecLMTensor {
    pub fn new(data: Vec<f64>) -> Result<Self, &'static str> {
        if data.is_empty() {
            return Err("Tensor data cannot be empty");
        }
        Ok(RecLMTensor { data })
    }

    pub fn sum(&self) -> f64 {
        self.data.iter().sum()
    }
}
