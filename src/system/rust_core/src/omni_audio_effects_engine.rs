// ===========================================================================
// OMNI AUDIO EFFECTS ENGINE (POLYLINGUAL REMEDIATION)
// ===========================================================================
// Absorbed From  : BillyDM/awesome-audio-dsp + Spotify/pedalboard concepts
// Logic Inherited: Rust / System Layer (Trait-Based Plugin Effect Chain)
// Domain Layer   : System (Rust Core)
// ===========================================================================

// By studying awesome-audio-dsp and pedalboard, Mother learned that
// professional audio effect chains are composed of discrete processing
// units (plugins) connected in series. Each plugin transforms a buffer
// of floating-point samples in-place. Rust's trait system is the ideal
// abstraction: each effect implements a common `AudioEffect` trait,
// and the chain owns them via dynamic dispatch (`Box<dyn AudioEffect>`).

/// Represents the sample rate and buffer configuration for processing.
#[derive(Debug, Clone, Copy)]
pub struct AudioConfig {
    pub sample_rate: f32,
    pub block_size: usize,
}

/// Every audio effect in the OMNI chain implements this trait.
pub trait AudioEffect {
    /// Process a buffer of interleaved stereo samples in-place.
    fn process(&mut self, buffer: &mut [f32], config: &AudioConfig);
    /// Return the effect's human-readable name.
    fn name(&self) -> &str;
    /// Reset all internal state (delay lines, filters, etc).
    fn reset(&mut self);
}

// ---------------------------------------------------------------------------
// Effect 1: Simple Gain (Volume Control)
// ---------------------------------------------------------------------------
pub struct GainEffect {
    pub gain_linear: f32,
}

impl GainEffect {
    pub fn new(gain_db: f32) -> Self {
        // dB to linear: 10^(dB/20)
        let gain_linear = 10.0_f32.powf(gain_db / 20.0);
        Self { gain_linear }
    }
}

impl AudioEffect for GainEffect {
    fn process(&mut self, buffer: &mut [f32], _config: &AudioConfig) {
        for sample in buffer.iter_mut() {
            *sample *= self.gain_linear;
        }
    }
    fn name(&self) -> &str { "Gain" }
    fn reset(&mut self) {}
}

// ---------------------------------------------------------------------------
// Effect 2: One-Pole Lowpass Filter
// ---------------------------------------------------------------------------
pub struct LowpassEffect {
    cutoff_hz: f32,
    coeff: f32,
    z1_left: f32,
    z1_right: f32,
}

impl LowpassEffect {
    pub fn new(cutoff_hz: f32, sample_rate: f32) -> Self {
        let rc = 1.0 / (2.0 * std::f32::consts::PI * cutoff_hz);
        let dt = 1.0 / sample_rate;
        let coeff = dt / (rc + dt);
        Self { cutoff_hz, coeff, z1_left: 0.0, z1_right: 0.0 }
    }
}

impl AudioEffect for LowpassEffect {
    fn process(&mut self, buffer: &mut [f32], _config: &AudioConfig) {
        // Interleaved stereo: [L, R, L, R, ...]
        let mut i = 0;
        while i < buffer.len() {
            // Left channel
            self.z1_left += self.coeff * (buffer[i] - self.z1_left);
            buffer[i] = self.z1_left;

            // Right channel (if stereo)
            if i + 1 < buffer.len() {
                self.z1_right += self.coeff * (buffer[i + 1] - self.z1_right);
                buffer[i + 1] = self.z1_right;
            }
            i += 2;
        }
    }
    fn name(&self) -> &str { "Lowpass" }
    fn reset(&mut self) {
        self.z1_left = 0.0;
        self.z1_right = 0.0;
    }
}

// ---------------------------------------------------------------------------
// Effect 3: Hard Clipper (Distortion / Limiter)
// ---------------------------------------------------------------------------
pub struct HardClipEffect {
    pub threshold: f32,
}

impl HardClipEffect {
    pub fn new(threshold: f32) -> Self {
        Self { threshold: threshold.abs() }
    }
}

impl AudioEffect for HardClipEffect {
    fn process(&mut self, buffer: &mut [f32], _config: &AudioConfig) {
        for sample in buffer.iter_mut() {
            if *sample > self.threshold {
                *sample = self.threshold;
            } else if *sample < -self.threshold {
                *sample = -self.threshold;
            }
        }
    }
    fn name(&self) -> &str { "HardClip" }
    fn reset(&mut self) {}
}

// ---------------------------------------------------------------------------
// Effect 4: Simple Delay Line
// ---------------------------------------------------------------------------
pub struct DelayEffect {
    delay_buffer: Vec<f32>,
    write_pos: usize,
    delay_samples: usize,
    feedback: f32,
    mix: f32,
}

impl DelayEffect {
    pub fn new(delay_ms: f32, feedback: f32, mix: f32, sample_rate: f32) -> Self {
        let delay_samples = ((delay_ms / 1000.0) * sample_rate) as usize;
        let buf_size = delay_samples.max(1);
        Self {
            delay_buffer: vec![0.0; buf_size],
            write_pos: 0,
            delay_samples: buf_size,
            feedback: feedback.clamp(0.0, 0.95),
            mix: mix.clamp(0.0, 1.0),
        }
    }
}

impl AudioEffect for DelayEffect {
    fn process(&mut self, buffer: &mut [f32], _config: &AudioConfig) {
        for sample in buffer.iter_mut() {
            let read_pos = (self.write_pos + self.delay_samples - 1) % self.delay_samples;
            let delayed = self.delay_buffer[read_pos];
            let input = *sample;
            self.delay_buffer[self.write_pos] = input + delayed * self.feedback;
            self.write_pos = (self.write_pos + 1) % self.delay_samples;
            *sample = input * (1.0 - self.mix) + delayed * self.mix;
        }
    }
    fn name(&self) -> &str { "Delay" }
    fn reset(&mut self) {
        self.delay_buffer.fill(0.0);
        self.write_pos = 0;
    }
}

// ---------------------------------------------------------------------------
// The Effect Chain: owns multiple effects, processes them in series.
// ---------------------------------------------------------------------------
pub struct OmniAudioEffectsEngine {
    effects: Vec<Box<dyn AudioEffect>>,
    config: AudioConfig,
}

impl OmniAudioEffectsEngine {
    pub fn new(sample_rate: f32, block_size: usize) -> Self {
        Self {
            effects: Vec::new(),
            config: AudioConfig { sample_rate, block_size },
        }
    }

    /// Add an effect to the end of the processing chain.
    pub fn add_effect(&mut self, effect: Box<dyn AudioEffect>) {
        self.effects.push(effect);
    }

    /// Process a buffer through the entire chain in series.
    pub fn process_chain(&mut self, buffer: &mut [f32]) {
        for effect in self.effects.iter_mut() {
            effect.process(buffer, &self.config);
        }
    }

    /// Reset all effects in the chain.
    pub fn reset_all(&mut self) {
        for effect in self.effects.iter_mut() {
            effect.reset();
        }
    }

    /// List all effects currently in the chain.
    pub fn list_effects(&self) -> Vec<&str> {
        self.effects.iter().map(|e| e.name()).collect()
    }

    pub fn diagnostics(&self) -> String {
        format!(
            "{{\"engine\": \"OmniAudioEffectsEngine\", \"layer\": \"Rust System\", \
             \"effects_count\": {}, \"sample_rate\": {}, \"block_size\": {}, \
             \"chain\": {:?}, \
             \"learned_logic\": [\"trait-based-plugin-dispatch\", \"in-place-buffer-mutation\", \
             \"serial-effect-chain\", \"delay-line-circular-buffer\"]}}",
            self.effects.len(), self.config.sample_rate, self.config.block_size,
            self.list_effects()
        )
    }
}

fn main() {
    let mut engine = OmniAudioEffectsEngine::new(44100.0, 512);

    engine.add_effect(Box::new(GainEffect::new(-6.0)));
    engine.add_effect(Box::new(LowpassEffect::new(2000.0, 44100.0)));
    engine.add_effect(Box::new(DelayEffect::new(250.0, 0.4, 0.3, 44100.0)));
    engine.add_effect(Box::new(HardClipEffect::new(0.8)));

    // Simulate a buffer of 8 stereo samples
    let mut buffer = vec![0.5, -0.3, 0.9, 0.1, -0.7, 0.4, 0.2, -0.6];
    engine.process_chain(&mut buffer);

    println!("{}", engine.diagnostics());
}
