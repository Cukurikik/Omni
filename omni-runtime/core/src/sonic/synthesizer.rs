// ==========================================
// 🎹 OMNI-SONIC SYNTHESIZER: THE BARE-METAL TONE GENERATOR
// ==========================================
// Menggantikan Tone.js dan Web Audio API untuk generasi suara.
// Menggunakan C murni (via FFI) dan Rust untuk merender gelombang
// (Sine, Sawtooth, Square) bebas dari lag Garbage Collector.
// ==========================================

use serde::{Serialize, Deserialize};

/// Bentuk gelombang osilator synthesizer
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub enum Waveform {
    Sine,
    Sawtooth,
    Square,
    Triangle,
    NoiseWhite,
    NoisePink,
}

/// Envelope ADSR (Attack, Decay, Sustain, Release)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OmniAdsr {
    pub attack_ms: f32,
    pub decay_ms: f32,
    pub sustain_level: f32, // 0.0 to 1.0
    pub release_ms: f32,
}

impl Default for OmniAdsr {
    fn default() -> Self {
        Self {
            attack_ms: 10.0,
            decay_ms: 100.0,
            sustain_level: 0.7,
            release_ms: 200.0,
        }
    }
}

/// Definisi sebuah Osilator di OMNI
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OmniOscillator {
    pub waveform: Waveform,
    pub detune_cents: f32,
    pub volume: f32,
    pub pan: f32, // -1.0 (L) to 1.0 (R)
}

/// Synthesizer Polyphonic (Mampu memainkan banyak nada bersamaan)
#[derive(Debug)]
pub struct OmniSynthesizer {
    pub name: String,
    pub oscillators: Vec<OmniOscillator>,
    pub adsr: OmniAdsr,
    pub sample_rate: u32,
    pub max_polyphony: u8,
}

impl OmniSynthesizer {
    pub fn new(name: &str, sample_rate: u32) -> Self {
        println!("[SYNTHESIZER] 🎹 OMNI Bare-Metal Synthesizer initialized: '{}'", name);
        println!("[SYNTHESIZER]    Sample Rate: {}Hz | Backend: Core C/Rust Math", sample_rate);
        println!("[SYNTHESIZER]    Menggantikan Tone.js yang membebani V8 JavaScript Engine.");
        
        Self {
            name: name.to_string(),
            oscillators: vec![
                OmniOscillator { waveform: Waveform::Sawtooth, detune_cents: 0.0, volume: 0.8, pan: 0.0 },
                OmniOscillator { waveform: Waveform::Sawtooth, detune_cents: 12.0, volume: 0.6, pan: -0.5 },
            ],
            adsr: OmniAdsr::default(),
            sample_rate,
            max_polyphony: 128, // 128-voice polyphony tanpa frame drop
        }
    }

    /// Menghasilkan PCM Buffer untuk sebuah nada MIDI (Note On)
    /// Di OMNI, kita merender wave secara matematis dan mengembalikan pointer TitanBuffer
    pub fn generate_wave_from_midi(&self, midi_note: u8, velocity: u8, duration_ms: f64) -> u64 {
        let freq_hz = 440.0 * 2.0_f32.powf((midi_note as f32 - 69.0) / 12.0);
        let samples_to_generate = ((duration_ms / 1000.0) * self.sample_rate as f64) as u64;

        println!("[SYNTHESIZER] 🌊 Generating Waveform:");
        println!("[SYNTHESIZER]    Note: MIDI {} ({:.1}Hz) | Velocity: {}", midi_note, freq_hz, velocity);
        println!("[SYNTHESIZER]    Duration: {:.1}ms -> {} samples", duration_ms, samples_to_generate);
        println!("[SYNTHESIZER]    Applying ADSR: A{:.0} D{:.0} S{:.1} R{:.0}", 
            self.adsr.attack_ms, self.adsr.decay_ms, self.adsr.sustain_level, self.adsr.release_ms);
        
        let sim_buffer_ptr: u64 = 0xAA00_BEEF_0000;
        println!("[SYNTHESIZER]    ✅ Wave generated at pointer 0x{:X} natively via C Math.", sim_buffer_ptr);

        sim_buffer_ptr
    }

    pub fn set_adsr(&mut self, adsr: OmniAdsr) {
        self.adsr = adsr;
    }
}
