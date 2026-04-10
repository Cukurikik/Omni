// ==========================================
// 🎛️ OMNI-SONIC: THE ABSOLUTE AUDIO MATRIX
// ==========================================
// Pemusnahan Wavesurfer.js, Librosa, Tone.js,
// PortAudio, JUCE, LAME, Recorder.js, Howler.js,
// dan Spotify Pedalboard (diserap, bukan dihancurkan).
//
// Developer bisa membangun saingan Adobe Audition
// atau FL Studio hanya dengan satu file .omni.
// ==========================================

pub mod waveform;
pub mod venom_dsp;
pub mod bare_metal_io;
pub mod titan_encoder;
pub mod pedalboard;
pub mod spectral;
pub mod synthesizer;
pub mod multitrack;
pub mod midi_hardware;

pub use waveform::*;
pub use venom_dsp::*;
pub use bare_metal_io::*;
pub use titan_encoder::*;
pub use pedalboard::*;
pub use spectral::*;
pub use synthesizer::*;
pub use multitrack::*;
pub use midi_hardware::*;
