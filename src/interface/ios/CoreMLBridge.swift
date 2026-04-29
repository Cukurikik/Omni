import CoreML
import Foundation

public class OmniCoreMLBridge {
    private var model: MLModel?

    public init(modelURL: URL) throws {
        let config = MLModelConfiguration()
        config.computeUnits = .all
        self.model = try MLModel(contentsOf: modelURL, configuration: config)
    }

    public func predict(inputFeatures: [String: Any]) throws -> MLFeatureProvider {
        guard let model = self.model else {
            throw NSError(domain: "OmniCoreML", code: 1, userInfo: [NSLocalizedDescriptionKey: "Model not loaded"])
        }
        let provider = try MLDictionaryFeatureProvider(dictionary: inputFeatures)
        return try model.prediction(from: provider)
    }
}
