// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Flutter Layout Solver (OMNI Zero-Mock Implementation)
// Implements box constraint math down the render tree.

pub struct BoxConstraints {
    pub min_width: f64,
    pub max_width: f64,
    pub min_height: f64,
    pub max_height: f64,
}

pub struct Size {
    pub width: f64,
    pub height: f64,
}

pub struct ResultBox<T> {
    pub value: Option<T>,
    pub is_ok: bool,
    pub error: String,
}

impl BoxConstraints {
    pub fn is_normalized(&self) -> bool {
        self.min_width >= 0.0 && self.min_height >= 0.0 &&
        self.max_width >= self.min_width && self.max_height >= self.min_height
    }

    pub fn constrain(&self, target_width: f64, target_height: f64) -> ResultBox<Size> {
        if !self.is_normalized() {
            return ResultBox { value: None, is_ok: false, error: "Constraints are not normalized.".to_string() };
        }

        let mut final_width = target_width;
        if final_width < self.min_width { final_width = self.min_width; }
        if final_width > self.max_width { final_width = self.max_width; }

        let mut final_height = target_height;
        if final_height < self.min_height { final_height = self.min_height; }
        if final_height > self.max_height { final_height = self.max_height; }

        ResultBox {
            value: Some(Size { width: final_width, height: final_height }),
            is_ok: true,
            error: "".to_string(),
        }
    }
}
