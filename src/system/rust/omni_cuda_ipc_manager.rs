use std::os::raw::{c_int, c_void};

// OMNI MOTHER: CUDA Inter-Process Communication (IPC) Manager
// Allows multiple processes (e.g., Python trainer, Rust dataloader, Go router) 
// to share GPU memory tensors without host copying.

#[repr(C)]
pub struct CudaIpcMemHandle {
    pub reserved: [u8; 64],
}

#[link(name = "cudart")]
extern "C" {
    fn cudaIpcGetMemHandle(handle: *mut CudaIpcMemHandle, devPtr: *mut c_void) -> c_int;
    fn cudaIpcOpenMemHandle(devPtr: *mut *mut c_void, handle: CudaIpcMemHandle, flags: c_uint) -> c_int;
    fn cudaIpcCloseMemHandle(devPtr: *mut c_void) -> c_int;
}

pub struct OmniCudaIpcManager;

impl OmniCudaIpcManager {
    pub fn export_tensor(device_ptr: *mut c_void) -> Result<CudaIpcMemHandle, String> {
        let mut handle = CudaIpcMemHandle { reserved: [0; 64] };
        unsafe {
            let status = cudaIpcGetMemHandle(&mut handle, device_ptr);
            if status != 0 {
                return Err(format!("CUDA Error: {}", status));
            }
        }
        Ok(handle)
    }

    pub fn import_tensor(handle: CudaIpcMemHandle) -> Result<*mut c_void, String> {
        let mut dev_ptr: *mut c_void = std::ptr::null_mut();
        unsafe {
            // cudaIpcMemLazyEnablePeerAccess = 1
            let status = cudaIpcOpenMemHandle(&mut dev_ptr, handle, 1);
            if status != 0 {
                return Err(format!("CUDA Error: {}", status));
            }
        }
        Ok(dev_ptr)
    }

    pub fn close_tensor(device_ptr: *mut c_void) -> Result<(), String> {
        unsafe {
            let status = cudaIpcCloseMemHandle(device_ptr);
            if status != 0 {
                return Err(format!("CUDA Error: {}", status));
            }
        }
        Ok(())
    }
}
