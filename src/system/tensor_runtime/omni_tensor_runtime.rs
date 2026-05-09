// @omni-layer System | @omni-lang Rust | @omni-batch 18 | @omni-semester 16
// @omni-description Rust GGML-style tensor runtime: arena allocator, tensor
// ops, and graph execution for transformer inference without heap allocation.

use std::alloc::{alloc, dealloc, Layout};

#[derive(Clone, Copy, Debug)]
pub enum DType { F32, F16, I8, I4 }

impl DType {
    pub fn size(&self) -> usize {
        match self { DType::F32 => 4, DType::F16 => 2, DType::I8 => 1, DType::I4 => 1 }
    }
}

pub struct Arena {
    ptr: *mut u8,
    capacity: usize,
    offset: usize,
}

impl Arena {
    pub fn new(capacity: usize) -> Self {
        let layout = Layout::from_size_align(capacity, 64).unwrap();
        let ptr = unsafe { alloc(layout) };
        Self { ptr, capacity, offset: 0 }
    }

    pub fn alloc(&mut self, size: usize) -> Option<*mut u8> {
        let aligned = (self.offset + 63) & !63;
        if aligned + size > self.capacity { return None; }
        let result = unsafe { self.ptr.add(aligned) };
        self.offset = aligned + size;
        Some(result)
    }

    pub fn reset(&mut self) { self.offset = 0; }
    pub fn used(&self) -> usize { self.offset }
}

impl Drop for Arena {
    fn drop(&mut self) {
        let layout = Layout::from_size_align(self.capacity, 64).unwrap();
        unsafe { dealloc(self.ptr, layout); }
    }
}

pub struct Tensor {
    pub data: *mut u8,
    pub shape: [usize; 4],
    pub ndim: usize,
    pub dtype: DType,
}

impl Tensor {
    pub fn nelements(&self) -> usize {
        self.shape[..self.ndim].iter().product()
    }

    pub fn nbytes(&self) -> usize {
        self.nelements() * self.dtype.size()
    }

    pub fn as_f32_slice(&self) -> &[f32] {
        assert!(matches!(self.dtype, DType::F32));
        unsafe { std::slice::from_raw_parts(self.data as *const f32, self.nelements()) }
    }

    pub fn as_f32_slice_mut(&mut self) -> &mut [f32] {
        assert!(matches!(self.dtype, DType::F32));
        unsafe { std::slice::from_raw_parts_mut(self.data as *mut f32, self.nelements()) }
    }
}

pub struct TensorGraph {
    arena: Arena,
    tensors: Vec<Tensor>,
}

impl TensorGraph {
    pub fn new(arena_mb: usize) -> Self {
        Self { arena: Arena::new(arena_mb * 1024 * 1024), tensors: Vec::new() }
    }

    pub fn new_tensor_2d(&mut self, dtype: DType, rows: usize, cols: usize) -> usize {
        let n = rows * cols;
        let size = n * dtype.size();
        let data = self.arena.alloc(size).expect("Arena OOM");
        unsafe { std::ptr::write_bytes(data, 0, size); }
        let t = Tensor { data, shape: [rows, cols, 0, 0], ndim: 2, dtype };
        self.tensors.push(t);
        self.tensors.len() - 1
    }

    pub fn get(&self, id: usize) -> &Tensor { &self.tensors[id] }
    pub fn get_mut(&mut self, id: usize) -> &mut Tensor { &mut self.tensors[id] }

    pub fn matmul(&mut self, a_id: usize, b_id: usize) -> usize {
        let ar = self.tensors[a_id].shape[0];
        let ac = self.tensors[a_id].shape[1];
        let bc = self.tensors[b_id].shape[1];
        let c_id = self.new_tensor_2d(DType::F32, ar, bc);
        let a = self.tensors[a_id].as_f32_slice();
        let b = self.tensors[b_id].as_f32_slice();
        let c = self.tensors[c_id].as_f32_slice_mut();
        for i in 0..ar {
            for j in 0..bc {
                let mut sum = 0.0f32;
                for k in 0..ac { sum += a[i * ac + k] * b[k * bc + j]; }
                c[i * bc + j] = sum;
            }
        }
        c_id
    }

    pub fn reset(&mut self) {
        self.arena.reset();
        self.tensors.clear();
    }

    pub fn memory_used(&self) -> usize { self.arena.used() }
}
