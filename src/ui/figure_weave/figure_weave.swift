import Foundation

// OMNI FIGURE WEAVE SWIFT ENGINE
// SwiftUI / CoreGraphics strict mapping for declarative SVG output array bounding.

public struct FigureWeaveResult<T> {
    public let value: T?
    public let error: String
    public let isOk: Bool
}

public class FigureWeaveSVGGenerator {
    private let maxCanvasWidth: Double
    private let maxCanvasHeight: Double

    public init(maxWidth: Double, maxHeight: Double) {
        self.maxCanvasWidth = maxWidth
        self.maxCanvasHeight = maxHeight
    }

    public func validateSVGCanvas(width: Double, height: Double) -> FigureWeaveResult<Double> {
        if width <= 0.0 || height <= 0.0 {
            return FigureWeaveResult(value: nil, error: "INVALID_ZERO_CANVAS_SIZE", isOk: false)
        }

        if width > maxCanvasWidth || height > maxCanvasHeight {
            return FigureWeaveResult(value: nil, error: "SVG_CANVAS_LIMIT_EXCEEDED", isOk: false)
        }

        let canvasArea = width * height
        return FigureWeaveResult(value: canvasArea, error: "", isOk: true)
    }
}
