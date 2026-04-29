use std::fmt;

// OMNI System Layer: Batch 05
// Rust structs bounds mappings predicting state boundaries isolating recursive multi-modal dialog nodes.

#[derive(Debug)]
pub enum DialogTrackerError {
    VectorMapZero,
    StateTreeOverflow,
}

impl fmt::Display for DialogTrackerError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match *self {
            DialogTrackerError::VectorMapZero => write!(f, "Node parameters limiting array checks mathematically zero."),
            DialogTrackerError::StateTreeOverflow => write!(f, "Logic matrix bounding limits exceeded geometry graph restrictions natively."),
        }
    }
}

pub struct MultimodalDialogTracker {
    max_tree_depth: usize,
    active_depth: usize,
}

impl MultimodalDialogTracker {
    pub fn new(max_depth: usize) -> Self {
        Self {
            max_tree_depth: max_depth,
            active_depth: 0,
        }
    }

    // Geometrically isolates matrices preventing system crashes recursively
    pub fn push_dialogue_state(&mut self, modal_vector_len: usize) -> Result<usize, DialogTrackerError> {
        if modal_vector_len == 0 {
            return Err(DialogTrackerError::VectorMapZero);
        }

        let depth_cost = 1 + (modal_vector_len / 512);

        if self.active_depth + depth_cost > self.max_tree_depth {
            return Err(DialogTrackerError::StateTreeOverflow);
        }

        self.active_depth += depth_cost;
        Ok(self.active_depth)
    }
}
