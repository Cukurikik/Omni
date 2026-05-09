// OMNI Interface — Swift CoreML Inference Client
// On-device transformer inference for Apple platforms.

import Foundation
import CoreML

@available(macOS 14.0, iOS 17.0, *)
public class OmniCoreMLEngine {
    private var model: MLModel?
    private let modelURL: URL
    private let queue = DispatchQueue(label: "omni.inference", qos: .userInitiated)
    private var stats = InferenceStats()

    public struct InferenceStats {
        var totalRequests: Int = 0
        var totalLatencyMs: Double = 0.0
        var errors: Int = 0
        var avgLatencyMs: Double { totalRequests > 0 ? totalLatencyMs / Double(totalRequests) : 0 }
    }

    public struct InferenceResult {
        let tokens: [Int]
        let text: String
        let latencyMs: Double
    }

    public init(modelPath: String) {
        self.modelURL = URL(fileURLWithPath: modelPath)
    }

    public func loadModel() throws {
        let config = MLModelConfiguration()
        config.computeUnits = .all  // Use Neural Engine + GPU + CPU
        self.model = try MLModel(contentsOf: modelURL, configuration: config)
    }

    public func predict(inputIds: [Int32], attentionMask: [Int32]) throws -> InferenceResult {
        guard let model = self.model else {
            throw OmniError.modelNotLoaded
        }

        let start = CFAbsoluteTimeGetCurrent()
        stats.totalRequests += 1

        let seqLen = inputIds.count
        let inputArray = try MLMultiArray(shape: [1, NSNumber(value: seqLen)], dataType: .int32)
        let maskArray = try MLMultiArray(shape: [1, NSNumber(value: seqLen)], dataType: .int32)

        for i in 0..<seqLen {
            inputArray[i] = NSNumber(value: inputIds[i])
            maskArray[i] = NSNumber(value: attentionMask[i])
        }

        let provider = try MLDictionaryFeatureProvider(dictionary: [
            "input_ids": MLFeatureValue(multiArray: inputArray),
            "attention_mask": MLFeatureValue(multiArray: maskArray)
        ])

        let prediction = try model.prediction(from: provider)

        guard let logits = prediction.featureValue(for: "logits")?.multiArrayValue else {
            throw OmniError.invalidOutput
        }

        // Greedy decode last position
        let vocabSize = logits.shape.last!.intValue
        var maxIdx = 0
        var maxVal = Float(logits[0].floatValue)
        let offset = (seqLen - 1) * vocabSize
        for i in 1..<vocabSize {
            let val = Float(logits[offset + i].floatValue)
            if val > maxVal { maxVal = val; maxIdx = i }
        }

        let latency = (CFAbsoluteTimeGetCurrent() - start) * 1000
        stats.totalLatencyMs += latency

        return InferenceResult(tokens: [maxIdx], text: "\(maxIdx)", latencyMs: latency)
    }

    public func getStats() -> InferenceStats { stats }

    public enum OmniError: Error {
        case modelNotLoaded
        case invalidOutput
        case tokenizationFailed
    }
}
