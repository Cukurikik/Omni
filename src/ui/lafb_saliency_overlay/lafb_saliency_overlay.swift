import Foundation
import CoreGraphics

public enum LAFBUIError: Error {
    case GeometricInvalidity(String)
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

/// OMNI Engine: lafb-overlay
/// Maps adaptive saliency fusion bounds to transparency alpha vectors on iOS UIKit.
public class LAFBOverlayEngine {
    private let mapAlphaCeiling: Double
    
    public init(alphaCeiling: Double = 0.85) {
        self.mapAlphaCeiling = alphaCeiling
    }

    public func calculateOverlayAlphaMask(heatmapIntensity: Double) -> Result<Double> {
        if heatmapIntensity < 0.0 || heatmapIntensity > 1.0 {
            return Result(error: LAFBUIError.GeometricInvalidity("Heatmap tensor limits exceeded 0.0 - 1.0 range bounds"))
        }

        // Apply a sigmoid or direct clipping bounds for iOS layer blend mode mapping
        let renderAlpha = min(heatmapIntensity * 1.2, self.mapAlphaCeiling)

        return Result(value: renderAlpha)
    }
}
