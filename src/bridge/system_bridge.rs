// ===========================================================================
// OMNI BRIDGE — SYSTEM ↔ ALL LAYERS INTERFACE
// ===========================================================================
// This module defines the FFI bridge contracts that allow UI, Network,
// Domain, and Compute layers to invoke System-layer primitives without
// violating layer segregation.
// ===========================================================================

/// Memory read request dispatched from any layer to the System layer.
pub struct MemoryReadRequest {
    pub address: u64,
    pub size: usize,
}

/// Memory read response returned by the System layer.
pub struct MemoryReadResponse {
    pub data: Vec<u8>,
    pub valid: bool,
}

/// RTTI lookup request for C++ object inspection.
pub struct RTTILookupRequest {
    pub vtable_address: u64,
}

pub struct RTTILookupResponse {
    pub class_name: String,
    pub field_count: u32,
}

/// Trait that any system-layer engine must implement to be bridgeable.
pub trait SystemBridge {
    fn read_memory(&self, req: MemoryReadRequest) -> Result<MemoryReadResponse, String>;
    fn identify_rtti(&self, req: RTTILookupRequest) -> Result<RTTILookupResponse, String>;
    fn health_check(&self) -> bool;
}

// Default no-op implementation for testing
pub struct NoOpSystemBridge;

impl SystemBridge for NoOpSystemBridge {
    fn read_memory(&self, req: MemoryReadRequest) -> Result<MemoryReadResponse, String> {
        Ok(MemoryReadResponse {
            data: vec![0xCC; req.size],
            valid: true,
        })
    }

    fn identify_rtti(&self, _req: RTTILookupRequest) -> Result<RTTILookupResponse, String> {
        Ok(RTTILookupResponse {
            class_name: "CUnknownObject".to_string(),
            field_count: 0,
        })
    }

    fn health_check(&self) -> bool {
        true
    }
}
