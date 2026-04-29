import Foundation
import CoreGraphics

public enum GANTreeUIError: Error {
    case spatialRenderOutOfBounds(String)
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
        if let err = error {
            throw err
        }
        return value!
    }
}

/// OMNI Engine: gantree-visualizer
/// Paints hierarchical GAN trees into the iOS CoreGraphics matrices.
public class GANTreeVisualizerEngine {
    private let maxTreeLevel: Int

    public init(maxLevel: Int = 5) {
        self.maxTreeLevel = maxLevel
    }

    public func calculateNodeSpatialGeometry(level: Int, childrenCount: Int) -> Result<CGSize> {
        if level <= 0 || childrenCount < 0 {
            return Result(error: GANTreeUIError.spatialRenderOutOfBounds("Hierarchical bounds inverted or negative"))
        }

        if level > maxTreeLevel {
            return Result(error: GANTreeUIError.spatialRenderOutOfBounds("Visualizer tree depth shattered iOS render bounds"))
        }

        let width = CGFloat(100.0 / Double(level))
        let height = width * 1.5

        if childrenCount > 10 {
           return Result(error: GANTreeUIError.spatialRenderOutOfBounds("Children count geometry overflows visual bounds"))
        }

        return Result(value: CGSize(width: width, height: height))
    }
}
