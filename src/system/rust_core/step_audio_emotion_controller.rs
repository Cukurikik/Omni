/// OMNI Step Audio Emotion Controller
/// Real-time filtering and emotion vector manipulation.

pub struct EmotionController {
    base_vector: [f32; 5],
}

impl EmotionController {
    pub fn new() -> Self {
        Self {
            base_vector: [0.0; 5], // Neutral
        }
    }

    pub fn blend_emotions(&self, target_emotion: &[f32; 5], alpha: f32) -> Result<[f32; 5], &'static str> {
        if alpha < 0.0 || alpha > 1.0 {
            return Err("Alpha must be between 0 and 1");
        }

        let mut blended = [0.0; 5];
        for i in 0..5 {
            blended[i] = self.base_vector[i] * (1.0 - alpha) + target_emotion[i] * alpha;
        }

        Ok(blended)
    }

    pub fn set_base_emotion(&mut self, new_base: [f32; 5]) {
        self.base_vector = new_base;
    }
}
