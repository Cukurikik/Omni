// OMNI MOTHER: Herbert-rs INT4/Q4 Quantization Engine

pub struct OmniHerbertQ4Block {
    pub d: f32, // delta/scaling factor
    pub qs: [u8; 16], // 32 4-bit nibbles
}

impl OmniHerbertQ4Block {
    pub fn dequantize(&self, output: &mut [f32]) {
        for i in 0..16 {
            let val = self.qs[i];
            let v0 = (val & 0x0F) as i32 - 8;
            let v1 = ((val >> 4) & 0x0F) as i32 - 8;
            
            output[i * 2] = v0 as f32 * self.d;
            output[i * 2 + 1] = v1 as f32 * self.d;
        }
    }
}
