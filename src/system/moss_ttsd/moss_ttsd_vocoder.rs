// MOSS-TTSD Vocoder Buffer Manager
pub struct OmniResult<T, E> { pub value: Option<T>, pub error: Option<E> }

pub struct AudioChunk { pub samples: Vec<f32>, pub sample_rate: u32, pub speaker_id: u32 }

pub struct VocoderBuffer {
    chunks: Vec<AudioChunk>,
    max_chunks: usize,
    max_duration_seconds: u32,
    current_duration_ms: u64,
}

impl VocoderBuffer {
    pub fn new() -> Self {
        Self { chunks: Vec::new(), max_chunks: 100000, max_duration_seconds: 3600, current_duration_ms: 0 }
    }

    pub fn push_chunk(&mut self, chunk: AudioChunk) -> OmniResult<usize, String> {
        if self.chunks.len() >= self.max_chunks {
            return OmniResult { value: None, error: Some("Buffer full".to_string()) };
        }
        let dur = (chunk.samples.len() as u64 * 1000) / chunk.sample_rate as u64;
        if self.current_duration_ms + dur > self.max_duration_seconds as u64 * 1000 {
            return OmniResult { value: None, error: Some("Exceeds 60min limit".to_string()) };
        }
        self.current_duration_ms += dur;
        self.chunks.push(chunk);
        OmniResult { value: Some(self.chunks.len()), error: None }
    }
}
