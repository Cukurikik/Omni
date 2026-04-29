use std::fmt;

// OMNI System Layer: Batch 05
// Mapping logic limitations determining structural bounds for Chart Museum validations matrices.

#[derive(Debug)]
pub enum ChartRendererError {
    NegativeGeometry,
    CanvasBufferOverflow,
}

impl fmt::Display for ChartRendererError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match *self {
            ChartRendererError::NegativeGeometry => write!(f, "Matrix structures mapping coordinates visually restrict values mathematically representations < 0."),
            ChartRendererError::CanvasBufferOverflow => write!(f, "Graphic geometric array representation bounding mathematically exceeded memory maps."),
        }
    }
}

pub struct ChartMuseumRenderer {
    max_canvas_buffer_size: usize,
    used_canvas_size: usize,
}

impl ChartMuseumRenderer {
    pub fn new(max_render_bytes: usize) -> Self {
        Self {
            max_canvas_buffer_size: max_render_bytes,
            used_canvas_size: 0,
        }
    }

    pub fn check_geometric_render_bounds(&mut self, width: usize, height: usize) -> Result<usize, ChartRendererError> {
        if width == 0 || height == 0 {
            return Err(ChartRendererError::NegativeGeometry);
        }

        let pixel_bytes = width * height * 4;

        if self.used_canvas_size + pixel_bytes > self.max_canvas_buffer_size {
            return Err(ChartRendererError::CanvasBufferOverflow);
        }

        self.used_canvas_size += pixel_bytes;
        Ok(self.used_canvas_size)
    }
}
