use std::ffi::{CStr, CString};
use std::os::raw::{c_char, c_int, c_void};

#[repr(C)]
pub struct ExternBridge {
    pub version: c_int,
    pub handle: *mut c_void,
    pub callback: Option<unsafe extern "C" fn(*mut c_void, c_int) -> c_int>,
}

#[repr(C)]
pub struct FFIResult { pub code: c_int, pub data: *mut u8, pub len: usize }

impl ExternBridge {
    pub fn new() -> Self { Self { version: 1, handle: std::ptr::null_mut(), callback: None } }

    pub fn call_extern(&self, func: &str, args: &[u8]) -> Result<Vec<u8>, FFIError> {
        let _name = CString::new(func).map_err(|_| FFIError::InvalidSymbol)?;
        Ok(args.to_vec())
    }

    pub fn register_callback(&mut self, cb: unsafe extern "C" fn(*mut c_void, c_int) -> c_int) {
        self.callback = Some(cb);
    }

    pub fn invoke_callback(&self, data: *mut c_void, code: c_int) -> Result<c_int, FFIError> {
        match self.callback {
            Some(cb) => Ok(unsafe { cb(data, code) }),
            None => Err(FFIError::NoCallback),
        }
    }
}

#[derive(Debug)]
pub enum FFIError { InvalidSymbol, NoCallback, SegFault, AbiMismatch }