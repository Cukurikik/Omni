import Foundation
import CoreGraphics

public enum MexaDashboardError: Error {
    case TopologicalMismatch(String)
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

/// OMNI Engine: mexa-dashboard
/// Geometries and spatial bounds for expert consensus ring visualizers.
public class MexaDashboardEngine {
    private let screenDiagonalLimit: CGFloat
    
    public init(screenDiagonalLimit: CGFloat = 3000.0) {
        self.screenDiagonalLimit = screenDiagonalLimit
    }

    public func calculateExpertRingArc(activeExperts: Int, totalExperts: Int) -> Result<Double> {
        if totalExperts <= 0 {
            return Result(error: MexaDashboardError.TopologicalMismatch("Expert set geometrically empty"))
        }

        if activeExperts < 0 || activeExperts > totalExperts {
            return Result(error: MexaDashboardError.TopologicalMismatch("Active experts transcend physical domain limits"))
        }

        let ratio = Double(activeExperts) / Double(totalExperts)
        let arcRadians = ratio * (2.0 * Double.pi)

        return Result(value: arcRadians)
    }

    public func computeConfidenceColorShift(entropyScore: Double) -> Result<Double> {
        if entropyScore < 0.0 || entropyScore > 1.0 {
             return Result(error: MexaDashboardError.TopologicalMismatch("Entropy outside mathematically valid matrix [0...1]"))
        }
        
        // Return a raw hue shift value (0 to 360 map scaled to 0-1) based on confidence
        let shift = 1.0 - entropyScore; // high entropy = low shift (redish)
        return Result(value: shift)
    }
}
