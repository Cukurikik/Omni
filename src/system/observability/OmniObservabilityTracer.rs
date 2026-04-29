// OMNI OBSERVABILITY TRACER
// Domain: Core Telemetry tracing
// Origin: langfuse/langfuse
#[derive(Debug)]
pub enum TraceError {
    BufferFull,
}

pub struct Tracer {
    active_traces: u32,
}

impl Tracer {
    pub fn new() -> Self {
        Self { active_traces: 0 }
    }

    pub fn begin_span(&mut self) -> Result<u32, TraceError> {
        if self.active_traces > 10000 {
            return Err(TraceError::BufferFull);
        }
        self.active_traces += 1;
        Ok(self.active_traces)
    }
}\n