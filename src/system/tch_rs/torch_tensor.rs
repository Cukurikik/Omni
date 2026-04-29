// OMNI Engine: tch-rs PyTorch zero-copy tensor bridge
use std::os::raw::c_void;

#[repr(C)]
pub struct C_Tensor {
    _private: [u8; 0],
}

extern "C" {
    fn atg_add(out: *mut *mut C_Tensor, self_: *mut C_Tensor, other: *mut C_Tensor, alpha: f64);
    fn at_free(tensor: *mut C_Tensor);
}

pub struct Tensor {
    c_tensor: *mut C_Tensor,
}

impl Tensor {
    pub fn add(&self, other: &Tensor) -> Tensor {
        let mut result: *mut C_Tensor = std::ptr::null_mut();
        unsafe {
            atg_add(&mut result, self.c_tensor, other.c_tensor, 1.0);
        }
        Tensor { c_tensor: result }
    }
}

impl Drop for Tensor {
    fn drop(&mut self) {
        unsafe {
            if !self.c_tensor.is_null() {
                at_free(self.c_tensor);
            }
        }
    }
}
