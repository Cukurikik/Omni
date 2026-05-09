// moe_tensor_serialize.swift — System / Interop
// Layer: System / Core — Swift Tensor Binary Serialization
//
// Serializes flat float arrays into a highly compact binary format.
// Used for fast IPC (Inter-Process Communication) on iOS/macOS, transferring 
// activations from the Swift app layer to the C++ CoreML/Metal backend.

import Foundation

public class MoETensorSerializer {
    
    public init() {}
    
    /// Serializes an array of Float32 into a raw Data buffer
    public func serializeFloat32(tensor: [Float]) -> Data {
        // Unsafe pointer copy for zero-overhead serialization
        let data = tensor.withUnsafeBufferPointer { buffer -> Data in
            if let baseAddress = buffer.baseAddress {
                return Data(bytes: baseAddress, count: buffer.count * MemoryLayout<Float>.stride)
            }
            return Data()
        }
        return data
    }
    
    /// Deserializes a raw Data buffer back into a Float32 array
    public func deserializeFloat32(data: Data) -> [Float] {
        let count = data.count / MemoryLayout<Float>.stride
        var tensor = [Float](repeating: 0.0, count: count)
        
        _ = tensor.withUnsafeMutableBufferPointer { buffer in
            data.copyBytes(to: buffer)
        }
        
        return tensor
    }
}
