pub struct Tensor {
    pub data: Vec<f32>,
    pub shape: Vec<usize>,
}

impl Tensor {
    pub fn new(shape: Vec<usize>) -> Self {
        let size = shape.iter().product();
        Self {
            data: vec![0.0; size],
            shape,
        }
    }

    pub fn relu(&mut self) {
        for x in self.data.iter_mut() {
            if *x < 0.0 {
                *x = 0.0;
            }
        }
    }

    pub fn leaky_relu(&mut self, alpha: f32) {
        for x in self.data.iter_mut() {
            if *x < 0.0 {
                *x *= alpha;
            }
        }
    }
}
