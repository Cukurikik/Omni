import Foundation
import CoreGraphics

public enum WaveformError: Error {
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

/// OMNI Engine: av-waveform-swift
/// Calculates spline bounds mapping for high-frequency audio visual arrays on iOS frames.
public class AVWaveformEngine {
    private let frameRateCap: Double
    
    public init(frameRateCap: Double = 120.0) {
        self.frameRateCap = frameRateCap
    }

    public func computePathReductionLimit(rawSampleCount: Int, screenWidthPixels: CGFloat) -> Result<Int> {
        if screenWidthPixels <= 0 {
            return Result(error: WaveformError.GeometricInvalidity("Screen width physically null"))
        }

        if rawSampleCount < 0 {
            return Result(error: WaveformError.GeometricInvalidity("Sample array inverted"))
        }

        // Logic: Rendering more points than pixels creates visual noise and wastes memory.
        let maxPointsPerPixel = 2
        let theoreticalPointLimit = Int(screenWidthPixels) * maxPointsPerPixel

        if rawSampleCount > theoreticalPointLimit {
             return Result(value: theoreticalPointLimit)
        }

        return Result(value: rawSampleCount)
    }

    public func evaluateRenderPhaseLag(renderTimeMs: Double) -> Result<Bool> {
        let frameBudgetMs = 1000.0 / frameRateCap
        let inBudget = renderTimeMs <= frameBudgetMs
        
        return Result(value: inBudget)
    }
}
