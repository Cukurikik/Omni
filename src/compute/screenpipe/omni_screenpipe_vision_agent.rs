// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Screenpipe Vision Agent (OMNI Zero-Mock Implementation)
// Implements bounding box stream reduction logic from OCR data.

pub struct Result<T, E> {
    pub value: Option<T>,
    pub error: Option<E>,
    pub is_ok: bool,
}

impl<T, E> Result<T, E> {
    pub fn ok(val: T) -> Self {
        Result { value: Some(val), error: None, is_ok: true }
    }
    
    pub fn err(e: E) -> Self {
        Result { value: None, error: Some(e), is_ok: false }
    }
}

pub struct OcrBox {
    pub x: f64,
    pub y: f64,
    pub width: f64,
    pub height: f64,
    pub text: String,
    pub confidence: f64,
}

pub struct ScreenpipeStreamProcessor;

impl ScreenpipeStreamProcessor {
    pub fn new() -> Self {
        ScreenpipeStreamProcessor
    }

    /// Merges horizontally adjacent OCR boxes into single lines
    pub fn merge_horizontal_boxes(mut boxes: Vec<OcrBox>, y_threshold: f64) -> Result<Vec<OcrBox>, String> {
        if boxes.is_empty() {
            return Result::err(String::from("No OCR boxes provided"));
        }

        // Sort by Y first, then X
        boxes.sort_by(|a, b| {
            let dy = a.y.partial_cmp(&b.y).unwrap();
            if dy == std::cmp::Ordering::Equal {
                a.x.partial_cmp(&b.x).unwrap()
            } else {
                dy
            }
        });

        let mut merged = Vec::new();
        let mut current_box = boxes.remove(0);

        for next_box in boxes {
            if (next_box.y - current_box.y).abs() <= y_threshold {
                // Same line, extend the width and concatenate text
                let new_width = (next_box.x + next_box.width) - current_box.x;
                current_box.width = new_width;
                current_box.text.push_str(" ");
                current_box.text.push_str(&next_box.text);
            } else {
                merged.push(current_box);
                current_box = next_box;
            }
        }
        merged.push(current_box);

        Result::ok(merged)
    }
}
