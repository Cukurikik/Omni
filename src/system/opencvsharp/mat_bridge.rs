// OMNI Engine: FFI Bridge for OpenCVSharp Mat object memory layout
#[repr(C)]
pub struct CvMat {
    pub rows: i32,
    pub cols: i32,
    pub type_: i32,
    pub data: *mut u8,
    pub step: usize,
}

impl CvMat {
    pub unsafe fn from_raw_parts(rows: i32, cols: i32, type_: i32, data: *mut u8, step: usize) -> Result<Self, &'static str> {
        if data.is_null() {
            return Err("Data pointer is null");
        }
        if rows <= 0 || cols <= 0 {
            return Err("Invalid dimensions");
        }
        Ok(CvMat {
            rows,
            cols,
            type_,
            data,
            step,
        })
    }

    pub fn read_pixel(&self, row: i32, col: i32) -> Result<u8, &'static str> {
        if row < 0 || row >= self.rows || col < 0 || col >= self.cols {
            return Err("Index out of bounds");
        }
        unsafe {
            let ptr = self.data.add((row as usize) * self.step + (col as usize));
            Ok(*ptr)
        }
    }
}
