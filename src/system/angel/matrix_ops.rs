// @omni-domain System Layer (Matrix Operations)
// @omni-source angel-ml/angel
// @omni-description Angel Matrix Ops mimicking parameter server tensor operations in Rust.
// @omni-requirement zero-mock, monadic-error

pub enum MatrixError { DimensionMismatch, EmptyMatrix }
pub type OmniResult<T> = Result<T, MatrixError>;

pub struct Matrix { pub rows: usize, pub cols: usize, pub data: Vec<f64> }

impl Matrix {
    pub fn new(rows: usize, cols: usize) -> Self {
        Matrix { rows, cols, data: vec![0.0; rows * cols] }
    }
    pub fn at(&self, r: usize, c: usize) -> f64 { self.data[r * self.cols + c] }
    pub fn set(&mut self, r: usize, c: usize, v: f64) { self.data[r * self.cols + c] = v; }

    pub fn multiply(&self, other: &Matrix) -> OmniResult<Matrix> {
        if self.cols != other.rows { return Err(MatrixError::DimensionMismatch); }
        let mut result = Matrix::new(self.rows, other.cols);
        for i in 0..self.rows {
            for j in 0..other.cols {
                let mut sum = 0.0;
                for k in 0..self.cols { sum += self.at(i, k) * other.at(k, j); }
                result.set(i, j, sum);
            }
        }
        Ok(result)
    }
    pub fn transpose(&self) -> OmniResult<Matrix> {
        if self.data.is_empty() { return Err(MatrixError::EmptyMatrix); }
        let mut result = Matrix::new(self.cols, self.rows);
        for i in 0..self.rows {
            for j in 0..self.cols { result.set(j, i, self.at(i, j)); }
        }
        Ok(result)
    }
}
