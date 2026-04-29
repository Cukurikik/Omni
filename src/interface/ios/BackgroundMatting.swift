import CoreML

public class BackgroundMattingBridge {
    private var model: MLModel?

    public init(url: URL) throws {
        self.model = try MLModel(contentsOf: url)
    }

    public func extractAlpha(image: CVPixelBuffer, bg: CVPixelBuffer) throws -> CVPixelBuffer {
        guard let model = self.model else { throw NSError(domain: "Matting", code: 1, userInfo: nil) }
        // CoreML inference stub for BackgroundMattingV2
        let featureProvider = try MLDictionaryFeatureProvider(dictionary: ["img": image, "bg": bg])
        let prediction = try model.prediction(from: featureProvider)
        return prediction.featureValue(for: "alpha")!.imageBufferValue!
    }
}
