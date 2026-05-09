pub struct HoiTensorOps;

impl HoiTensorOps {
    pub fn compute_interaction_matrix(hand: &[f32], object: &[f32]) -> Result<Vec<f32>, String> {
        if hand.len() != object.len() {
            return Err("Dimension mismatch between hand and object vectors".to_string());
        }
        
        let mut matrix = Vec::with_capacity(hand.len());
        for i in 0..hand.len() {
            matrix.push(hand[i] * object[i]);
        }
        Ok(matrix)
    }
}
