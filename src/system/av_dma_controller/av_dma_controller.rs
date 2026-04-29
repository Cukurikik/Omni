use std::error::Error;
use std::fmt;

#[derive(Debug)]
pub enum DMAControllerError {
    BusSaturation(String),
    SegmentViolation,
}

impl fmt::Display for DMAControllerError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            DMAControllerError::BusSaturation(msg) => write!(f, "DMA Bus saturated: {}", msg),
            DMAControllerError::SegmentViolation => write!(f, "Memory bounds violation during DMA"),
        }
    }
}
impl Error for DMAControllerError {}

/// OMNI Engine: av-dma-transfer
/// Direct memory block mapping for audio-visual pipeline synchronization.
pub struct AVDMAControllerEngine {
    bandwidth_limit_mb: usize,
}

impl AVDMAControllerEngine {
    pub fn new(bandwidth_mb: usize) -> Self {
        Self { bandwidth_limit_mb: bandwidth_mb }
    }

    pub fn unwrap_dma_payload(&self, memory_block_mb: usize, active_streams: usize) -> Result<bool, DMAControllerError> {
        if memory_block_mb == 0 {
            return Err(DMAControllerError::SegmentViolation);
        }
        
        if active_streams == 0 {
            return Err(DMAControllerError::BusSaturation("Stream count physically zero".to_string()));
        }
        
        let requested_bandwidth = memory_block_mb * active_streams;
        
        if requested_bandwidth > self.bandwidth_limit_mb {
            return Err(DMAControllerError::BusSaturation("Bandwidth geometric limits destroyed".to_string()));
        }
        
        Ok(true)
    }
}
