//=============================================================================
// OMNI SYSTEM LAYER — TENSOR SHAPE & STRIDES (RUST)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: Memory-safe representation of Tensor Shapes and Strides 
//              for multi-dimensional array operations.
//=============================================================================

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TensorShape {
    pub dims: Vec<usize>,
    pub strides: Vec<usize>,
}

impl TensorShape {
    /// Creates a new contiguous tensor shape.
    pub fn new_contiguous(dims: Vec<usize>) -> Self {
        let mut strides = vec![0; dims.len()];
        let mut current_stride = 1;
        
        for i in (0..dims.len()).rev() {
            strides[i] = current_stride;
            current_stride *= dims[i];
        }
        
        Self { dims, strides }
    }

    /// Calculates the flat 1D offset for multi-dimensional indices.
    #[inline(always)]
    pub fn calculate_offset(&self, indices: &[usize]) -> Option<usize> {
        if indices.len() != self.dims.len() {
            return None;
        }

        let mut offset = 0;
        for (i, &idx) in indices.iter().enumerate() {
            if idx >= self.dims[i] {
                return None; // Index out of bounds
            }
            offset += idx * self.strides[i];
        }

        Some(offset)
    }

    pub fn total_elements(&self) -> usize {
        self.dims.iter().product()
    }
}
