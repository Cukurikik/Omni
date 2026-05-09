import CoreML
import Foundation

class OmniCoreMLDelegate {
    var model: MLModel?

    init(modelPath: String) throws {
        let url = URL(fileURLWithPath: modelPath)
        let config = MLModelConfiguration()
        config.computeUnits = .all
        
        self.model = try MLModel(contentsOf: url, configuration: config)
        print("OMNI CoreML Delegate initialized")
    }

    func predict(inputArray: [Float]) throws -> [Float] {
        guard let model = self.model else {
            throw NSError(domain: "OmniCoreML", code: 1, userInfo: [NSLocalizedDescriptionKey: "Model not loaded"])
        }
        
        let multiArray = try MLMultiArray(shape: [NSNumber(value: inputArray.count)], dataType: .float32)
        for (index, element) in inputArray.enumerated() {
            multiArray[index] = NSNumber(value: element)
        }
        
        let featureProvider = try MLDictionaryFeatureProvider(dictionary: ["input": multiArray])
        let prediction = try model.prediction(from: featureProvider)
        
        guard let outputArray = prediction.featureValue(for: "output")?.multiArrayValue else {
            return []
        }
        
        var result: [Float] = []
        for i in 0..<outputArray.count {
            result.append(outputArray[i].floatValue)
        }
        return result
    }
}
