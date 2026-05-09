use std::alloc::{alloc, dealloc, Layout};
use std::ptr::NonNull;

pub struct MedicalImageAllocator {
    ptr: NonNull<u8>,
    layout: Layout,
    size: usize,
}

impl MedicalImageAllocator {
    pub fn new(size: usize) -> Result<Self, String> {
        let layout = Layout::array::<u8>(size).map_err(|e| e.to_string())?;
        let ptr = unsafe { alloc(layout) };
        
        let non_null_ptr = NonNull::new(ptr).ok_or("Allocation failed for Medical Image")?;
        
        Ok(MedicalImageAllocator {
            ptr: non_null_ptr,
            layout,
            size,
        })
    }
}

impl Drop for MedicalImageAllocator {
    fn drop(&mut self) {
        unsafe {
            dealloc(self.ptr.as_ptr(), self.layout);
        }
    }
}
