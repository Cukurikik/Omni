/// OMNI Document Layout Parser
/// Safe Rust parser for processing bounding box relationships in segmented documents.

#[derive(Debug, Clone)]
pub struct BoundingBox {
    pub x1: f32,
    pub y1: f32,
    pub x2: f32,
    pub y2: f32,
    pub label_id: u32,
}

pub struct DocLayoutParser {
    pub iou_threshold: f32,
}

impl DocLayoutParser {
    pub fn new(iou_threshold: f32) -> Self {
        Self { iou_threshold }
    }

    pub fn compute_iou(&self, box_a: &BoundingBox, box_b: &BoundingBox) -> f32 {
        let x_left = box_a.x1.max(box_b.x1);
        let y_top = box_a.y1.max(box_b.y1);
        let x_right = box_a.x2.min(box_b.x2);
        let y_bottom = box_a.y2.min(box_b.y2);

        if x_right < x_left || y_bottom < y_top {
            return 0.0;
        }

        let intersection_area = (x_right - x_left) * (y_bottom - y_top);
        let area_a = (box_a.x2 - box_a.x1) * (box_a.y2 - box_a.y1);
        let area_b = (box_b.x2 - box_b.x1) * (box_b.y2 - box_b.y1);

        intersection_area / (area_a + area_b - intersection_area)
    }

    pub fn apply_nms(&self, boxes: &mut Vec<BoundingBox>) -> Vec<BoundingBox> {
        let mut keep = Vec::new();
        // Assuming boxes are sorted by confidence before passing to NMS
        let mut active = vec![true; boxes.len()];

        for i in 0..boxes.len() {
            if !active[i] { continue; }
            keep.push(boxes[i].clone());
            
            for j in (i + 1)..boxes.len() {
                if active[j] && self.compute_iou(&boxes[i], &boxes[j]) > self.iou_threshold {
                    active[j] = false;
                }
            }
        }
        
        keep
    }
}
