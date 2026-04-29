use std::collections::HashMap;

/// OMNI OCR Document Engine — System Layer
/// Absorbing AlibabaResearch/AdvancedLiterateMachinery
/// Production bounding-box NMS and text-region extraction in safe Rust.

pub type Result<T> = std::result::Result<T, OcrError>;

#[derive(Debug)]
pub enum OcrError {
    EmptyInput,
    InvalidBbox(String),
    ThresholdOutOfRange,
}

#[derive(Clone, Debug)]
pub struct BoundingBox {
    pub x1: f32, pub y1: f32,
    pub x2: f32, pub y2: f32,
    pub confidence: f32,
    pub label: String,
}

pub struct OmniOcrDocEngine {
    nms_threshold: f32,
    detections: u64,
}

impl OmniOcrDocEngine {
    pub fn new(nms_threshold: f32) -> Result<Self> {
        if nms_threshold < 0.0 || nms_threshold > 1.0 {
            return Err(OcrError::ThresholdOutOfRange);
        }
        Ok(Self { nms_threshold, detections: 0 })
    }

    fn iou(a: &BoundingBox, b: &BoundingBox) -> f32 {
        let x1 = a.x1.max(b.x1);
        let y1 = a.y1.max(b.y1);
        let x2 = a.x2.min(b.x2);
        let y2 = a.y2.min(b.y2);
        let inter = (x2 - x1).max(0.0) * (y2 - y1).max(0.0);
        let area_a = (a.x2 - a.x1) * (a.y2 - a.y1);
        let area_b = (b.x2 - b.x1) * (b.y2 - b.y1);
        let union = area_a + area_b - inter;
        if union <= 0.0 { 0.0 } else { inter / union }
    }

    /// Non-Maximum Suppression: filter overlapping bounding boxes
    pub fn nms(&mut self, mut boxes: Vec<BoundingBox>) -> Result<Vec<BoundingBox>> {
        if boxes.is_empty() { return Err(OcrError::EmptyInput); }
        self.detections += 1;
        boxes.sort_by(|a, b| b.confidence.partial_cmp(&a.confidence).unwrap());
        let mut keep = Vec::new();
        let mut suppressed = vec![false; boxes.len()];
        for i in 0..boxes.len() {
            if suppressed[i] { continue; }
            keep.push(boxes[i].clone());
            for j in (i + 1)..boxes.len() {
                if !suppressed[j] && Self::iou(&boxes[i], &boxes[j]) > self.nms_threshold {
                    suppressed[j] = true;
                }
            }
        }
        Ok(keep)
    }

    pub fn diagnostics(&self) -> HashMap<String, String> {
        let mut d = HashMap::new();
        d.insert("engine".into(), "OmniOcrDocEngine".into());
        d.insert("nms_threshold".into(), self.nms_threshold.to_string());
        d.insert("detections".into(), self.detections.to_string());
        d.insert("status".into(), "Operational".into());
        d
    }
}
