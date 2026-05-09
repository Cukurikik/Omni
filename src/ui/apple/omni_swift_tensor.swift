import CoreML
import Foundation
import Accelerate

/// Omni Swift Tensor Core (Swift)
/// Interface & Native Compute Layer
/// Leverages Apple's Accelerate framework (BNNS/vDSP) for hardware-accelerated 
/// transformer inference on macOS/iOS without bridging to C++.

public class OmniSwiftTensor {
    public let shape: [Int]
    public var data: [Float]
    
    public init(shape: [Int], data: [Float]? = nil) {
        self.shape = shape
        let count = shape.reduce(1, *)
        self.data = data ?? Array(repeating: 0.0, count: count)
    }
    
    /// Highly optimized dot product utilizing Accelerate vDSP
    public func dot(_ other: OmniSwiftTensor) -> Float {
        precondition(self.data.count == other.data.count, "Tensor shapes must match for dot product")
        var result: Float = 0.0
        vDSP_dotpr(self.data, 1, other.data, 1, &result, vDSP_Length(self.data.count))
        return result
    }
    
    /// Softmax activation using Accelerate vecLib
    public mutating func softmax() {
        var maxVal: Float = 0.0
        vDSP_maxv(self.data, 1, &maxVal, vDSP_Length(self.data.count))
        
        // Subtract max for numerical stability
        var negMax = -maxVal
        vDSP_vsadd(self.data, 1, &negMax, &self.data, 1, vDSP_Length(self.data.count))
        
        // Exponentiate
        var count = Int32(self.data.count)
        vvexpf(&self.data, self.data, &count)
        
        // Sum and divide
        var sum: Float = 0.0
        vDSP_sve(self.data, 1, &sum, vDSP_Length(self.data.count))
        
        var sum_reciprocal = 1.0 / sum
        vDSP_vsmul(self.data, 1, &sum_reciprocal, &self.data, 1, vDSP_Length(self.data.count))
    }
}
