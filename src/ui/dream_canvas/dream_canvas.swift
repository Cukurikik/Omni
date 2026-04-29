import Foundation
import CoreGraphics

public enum DreamCanvasError: Error {
    case GeometricInvalidity(String)
    case RenderMemoryLock
}

public struct Result<T> {
    public let value: T?
    public let error: Error?

    public init(value: T) {
        self.value = value
        self.error = nil
    }

    public init(error: Error) {
        self.value = nil
        self.error = error
    }

    public func isOk() -> Bool {
        return error == nil
    }

    public func unwrap() throws -> T {
        if let error = error {
            throw error
        }
        return value!
    }
}

/// OMNI Engine: dream-canvas
/// Viewport density rendering logic for masked diffusion geometries on iOS bounds.
public class DreamCanvasEngine {
    private let maxResolutionLimit: CGFloat
    
    public init(maxResolutionLimit: CGFloat = 8192.0) {
        self.maxResolutionLimit = maxResolutionLimit
    }

    public func calculateViewportMemoryTax(width: CGFloat, height: CGFloat, layers: Int) -> Result<Double> {
        if width <= 0 || height <= 0 {
            return Result(error: DreamCanvasError.GeometricInvalidity("Screen dimensions logically crushed"))
        }

        if width > maxResolutionLimit || height > maxResolutionLimit {
             return Result(error: DreamCanvasError.GeometricInvalidity("Resolution exceeds memory bounds"))
        }

        if layers <= 0 {
            return Result(error: DreamCanvasError.GeometricInvalidity("Viewport requires at least 1 functional layer"))
        }

        // Calculate theoretical bits required
        let pixelCount = width * height
        let bitsPerLayer = pixelCount * 32.0 // Assuming RGBA-8
        let totalMegabytes = (bitsPerLayer * Double(layers)) / (8.0 * 1024 * 1024)

        if totalMegabytes > 1024.0 {
            return Result(error: DreamCanvasError.RenderMemoryLock) // Reject if > 1GB memory alloc
        }

        return Result(value: totalMegabytes)
    }

    public func validateMaskAlphaChannel(alphaMap: [Double]) -> Result<Bool> {
        let activeAlphas = alphaMap.filter { $0 > 0.0 }.count
        if activeAlphas == 0 {
             return Result(error: DreamCanvasError.GeometricInvalidity("Alpha mapped entirely to vacuum."))
        }
        return Result(value: true)
    }
}
