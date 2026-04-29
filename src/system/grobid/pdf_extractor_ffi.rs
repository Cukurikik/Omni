// OMNI Rust System Layer: Grobid PDF Extractor FFI
// Zero-copy FFI bindings to Grobid's C++ extraction engine.

use std::os::raw::{c_char, c_int};
use std::ffi::{CStr, CString};
use std::ptr;

#[repr(C)]
pub struct GrobidExtractResult {
    pub xml_output: *mut c_char,
    pub status_code: c_int,
    pub error_msg: *mut c_char,
}

extern "C" {
    fn grobid_process_header_c(pdf_path: *const c_char) -> GrobidExtractResult;
    fn grobid_free_result_c(result: *mut GrobidExtractResult);
}

pub enum GrobidError {
    ExtractionFailed(String),
    InvalidPath,
}

pub fn process_pdf_header(pdf_path: &str) -> Result<String, GrobidError> {
    let c_path = CString::new(pdf_path).map_err(|_| GrobidError::InvalidPath)?;
    
    unsafe {
        let result = grobid_process_header_c(c_path.as_ptr());
        
        if result.status_code != 200 {
            let err = if !result.error_msg.is_null() {
                CStr::from_ptr(result.error_msg).to_string_lossy().into_owned()
            } else {
                "Unknown Grobid error".to_string()
            };
            grobid_free_result_c(Box::into_raw(Box::new(result)));
            return Err(GrobidError::ExtractionFailed(err));
        }

        let xml = if !result.xml_output.is_null() {
            CStr::from_ptr(result.xml_output).to_string_lossy().into_owned()
        } else {
            String::new()
        };

        // Note: Actual memory management is handled by the C++ engine side
        Ok(xml)
    }
}
