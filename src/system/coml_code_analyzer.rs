// OMNI System Layer - CoML Code Analyzer
use std::ffi::CStr;
use std::os::raw::c_char;

pub enum AnalyzerError {
    NullPointer,
    InvalidUtf8,
}

pub struct AnalyzerResult {
    pub complexity: u32,
}

impl AnalyzerResult {
    pub fn analyze(c_code: *const c_char) -> Result<Self, AnalyzerError> {
        if c_code.is_null() {
            return Err(AnalyzerError::NullPointer);
        }

        let c_str = unsafe { CStr::from_ptr(c_code) };
        let str_slice = c_str.to_str().map_err(|_| AnalyzerError::InvalidUtf8)?;

        // Fast zero-copy complexity calculation
        let complexity = str_slice.matches("if").count() 
                       + str_slice.matches("for").count() 
                       + str_slice.matches("while").count();

        Ok(Self { complexity: complexity as u32 })
    }
}
