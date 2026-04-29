import Foundation
import SwiftUI

public enum FeelingBlueUIError: Error {
    case emotionThemeBoundsBroken(String)
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

/// OMNI Engine: feeling-blue-theme
/// SwiftUI view modifier constraints mapping emotion metrics to UI gradients.
public class FeelingBlueThemeEngine {
    private let minBrightnessLevel: Double

    public init(minBrightness: Double = 0.2) {
        self.minBrightnessLevel = minBrightness
    }

    public func mapEmotionToColorGradient(melancholyScore: Double) -> Result<Color> {
        if melancholyScore < 0.0 || melancholyScore > 1.0 {
            return Result(error: FeelingBlueUIError.emotionThemeBoundsBroken("Emotion UI matrix exceeded 0.0-1.0 boundary geometry"))
        }

        // Higher melancholy = deeper blue
        let unmappedBrightness = 1.0 - (melancholyScore * 0.8)
        let finalBrightness = max(unmappedBrightness, minBrightnessLevel)

        return Result(value: Color(red: 0.1, green: 0.1, blue: melancholyScore, opacity: finalBrightness))
    }
}
