// OMNI MOTHER: NUMA-Aware Allocator
// Binds memory allocations to specific CPU sockets to avoid cross-QPI latency when feeding GPUs.

#[cfg(target_os = "linux")]
extern "C" {
    fn numa_alloc_onnode(size: usize, node: i32) -> *mut u8;
    fn numa_free(ptr: *mut u8, size: usize);
}

pub struct OmniNumaAllocator;

impl OmniNumaAllocator {
    pub fn alloc(size: usize, node_id: i32) -> Result<*mut u8, String> {
        #[cfg(target_os = "linux")]
        unsafe {
            let ptr = numa_alloc_onnode(size, node_id);
            if ptr.is_null() {
                return Err("NUMA allocation failed".to_string());
            }
            Ok(ptr)
        }
        
        #[cfg(not(target_os = "linux"))]
        {
            // Fallback for Windows/macOS
            let mut vec = Vec::with_capacity(size);
            let ptr = vec.as_mut_ptr();
            std::mem::forget(vec);
            Ok(ptr)
        }
    }

    pub fn free(ptr: *mut u8, size: usize) {
        #[cfg(target_os = "linux")]
        unsafe {
            numa_free(ptr, size);
        }
        
        #[cfg(not(target_os = "linux"))]
        unsafe {
            let _ = Vec::from_raw_parts(ptr, 0, size);
        }
    }
}
