// OMNI System Layer: valle_audio_codec.rs
// Implements Zero-Shot TTS Audio Codec buffer management.
// Hardware bounds: Max 30 seconds of audio at 24kHz (720,000 frames)

use omni_std::result::{OmniResult, OmniError};

const SAMPLE_RATE: usize = 24000;
const MAX_SECONDS: usize = 30;
const MAX_FRAMES: usize = SAMPLE_RATE * MAX_SECONDS;

pub struct ValleAudioBuffer {
    pcm_data: [f32; MAX_FRAMES],
    head: usize,
}

impl ValleAudioBuffer {
    pub fn new() -> OmniResult<Self> {
        Ok(Self {
            pcm_data: [0.0; MAX_FRAMES],
            head: 0,
        })
    }

    /// Appends generated codec frames to the PCM buffer.
    pub fn append_frames(&mut self, frames: &[f32]) -> OmniResult<()> {
        if self.head + frames.len() > MAX_FRAMES {
            return Err(OmniError::BufferOverflow(
                "VALL-E audio synthesis exceeds physical 30-second boundary."
            ));
        }

        // Vectorized copy 
        self.pcm_data[self.head..self.head + frames.len()].copy_from_slice(frames);
        self.head += frames.len();

        Ok(())
    }

    pub fn get_audio_slice(&self) -> &[f32] {
        &self.pcm_data[..self.head]
    }

    pub fn clear(&mut self) {
        self.head = 0;
    }
}

// FFI exposure for Swift/HTML layers
#[no_mangle]
pub extern "C" fn omni_valle_append(buffer_ptr: *mut ValleAudioBuffer, data: *const f32, len: usize) -> i32 {
    if buffer_ptr.is_null() || data.is_null() {
        return 1;
    }
    
    let buffer = unsafe { &mut *buffer_ptr };
    let slice = unsafe { std::slice::from_raw_parts(data, len) };
    
    match buffer.append_frames(slice) {
        Ok(_) => 0,
        Err(_) => 2, // Map overflow to error code 2
    }
}
