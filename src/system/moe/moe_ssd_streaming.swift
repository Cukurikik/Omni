// moe_ssd_streaming.swift — System / Apple Silicon Memory
// Layer: System / OS — Mac Unified Memory Streaming
//
// Implements SSD-to-Unified-Memory streaming for MoE models on Apple Silicon
// (similar to MLX-Flash). By leveraging the unified memory architecture, we can 
// bypass CPU bounce-buffers and stream inactive experts directly from SSD to GPU 
// memory mappings utilizing Metal.

import Foundation
import Metal

public enum StreamingError: Error {
    case deviceNotFound
    case bufferAllocationFailed
    case fileMappingFailed
}

public class MoESSDStreamer {
    private let device: MTLDevice
    private let commandQueue: MTLCommandQueue
    private var expertFileDescriptors: [Int: Int32] = [:]
    private var mappedPointers: [Int: UnsafeMutableRawPointer] = [:]
    
    public init() throws {
        guard let mtlDevice = MTLCreateSystemDefaultDevice() else {
            throw StreamingError.deviceNotFound
        }
        self.device = mtlDevice
        guard let queue = device.makeCommandQueue() else {
            throw StreamingError.deviceNotFound
        }
        self.commandQueue = queue
    }
    
    /// Pre-maps an expert's weights from SSD into the virtual address space.
    /// Does not eagerly load into RAM.
    public func mmapExpert(expertId: Int, filePath: String) throws {
        let fd = open(filePath, O_RDONLY)
        if fd < 0 {
            throw StreamingError.fileMappingFailed
        }
        
        var statBuf = stat()
        fstat(fd, &statBuf)
        let size = Int(statBuf.st_size)
        
        // Map file directly. MAP_SHARED allows kernel page caching.
        let ptr = mmap(nil, size, PROT_READ, MAP_SHARED, fd, 0)
        if ptr == MAP_FAILED {
            close(fd)
            throw StreamingError.fileMappingFailed
        }
        
        expertFileDescriptors[expertId] = fd
        if let validPtr = ptr {
            mappedPointers[expertId] = validPtr
            // Advise kernel we will need this (trigger asynchronous read-ahead)
            madvise(validPtr, size, MADV_WILLNEED)
        }
    }
    
    /// Wraps the mapped SSD pointer into a Metal Buffer utilizing Unified Memory.
    /// StorageModeShared allows the GPU to access the memory mapped from SSD,
    /// triggering page faults handled by the Apple Silicon memory controller.
    public func getMetalBufferForExpert(expertId: Int, byteSize: Int) throws -> MTLBuffer {
        guard let ptr = mappedPointers[expertId] else {
            throw StreamingError.bufferAllocationFailed
        }
        
        // NoCopy initialization maps the existing virtual memory directly into Metal.
        // On Apple Silicon, this allows the GPU to stream weights directly from the SSD page cache.
        guard let buffer = device.makeBuffer(bytesNoCopy: ptr,
                                             length: byteSize,
                                             options: .storageModeShared,
                                             deallocator: nil) else {
            throw StreamingError.bufferAllocationFailed
        }
        
        return buffer
    }
    
    /// Unmaps and cleans up an expert.
    public func unmapExpert(expertId: Int, byteSize: Int) {
        if let ptr = mappedPointers[expertId] {
            munmap(ptr, byteSize)
            mappedPointers.removeValue(forKey: expertId)
        }
        
        if let fd = expertFileDescriptors[expertId] {
            close(fd)
            expertFileDescriptors.removeValue(forKey: expertId)
        }
    }
}
