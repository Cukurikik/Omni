// OMNI Interface Layer — Swift On-Device Inference Engine
// CoreML-integrated transformer inference for Apple platforms.

import Foundation
#if canImport(CoreML)
import CoreML
#endif
#if canImport(Accelerate)
import Accelerate
#endif

// MARK: - Inference Configuration
struct OmniInferenceConfig {
    var maxTokens: Int = 256
    var temperature: Float = 0.7
    var topP: Float = 0.9
    var topK: Int = 50
    var repetitionPenalty: Float = 1.1
    var stopTokenIds: [Int] = []
}

// MARK: - Tensor Operations (Accelerate-backed)
struct OmniTensor {
    var data: [Float]
    let shape: [Int]
    
    var count: Int { data.count }
    
    static func zeros(shape: [Int]) -> OmniTensor {
        let count = shape.reduce(1, *)
        return OmniTensor(data: [Float](repeating: 0.0, count: count), shape: shape)
    }
    
    mutating func softmax() {
        var maxVal: Float = -Float.infinity
        vDSP_maxv(data, 1, &maxVal, vDSP_Length(data.count))
        
        var negMax = -maxVal
        vDSP_vsadd(data, 1, &negMax, &data, 1, vDSP_Length(data.count))
        
        var count = Int32(data.count)
        vvexpf(&data, data, &count)
        
        var sum: Float = 0.0
        vDSP_sve(data, 1, &sum, vDSP_Length(data.count))
        
        vDSP_vsdiv(data, 1, &sum, &data, 1, vDSP_Length(data.count))
    }
    
    func dotProduct(with other: OmniTensor) -> Float {
        var result: Float = 0.0
        vDSP_dotpr(data, 1, other.data, 1, &result, vDSP_Length(min(data.count, other.data.count)))
        return result
    }
    
    mutating func rmsNorm(weight: [Float], eps: Float = 1e-6) {
        var sumSq: Float = 0.0
        vDSP_svesq(data, 1, &sumSq, vDSP_Length(data.count))
        let rms = 1.0 / sqrt(sumSq / Float(data.count) + eps)
        
        var scale = rms
        vDSP_vsmul(data, 1, &scale, &data, 1, vDSP_Length(data.count))
        vDSP_vmul(data, 1, weight, 1, &data, 1, vDSP_Length(data.count))
    }
}

// MARK: - Generation Result
struct GenerationResult {
    let text: String
    let tokenIds: [Int]
    let tokensGenerated: Int
    let latencyMs: Double
    let finishReason: FinishReason
    
    enum FinishReason {
        case stop
        case maxTokens
        case error(String)
    }
}

// MARK: - On-Device Inference Engine
class OmniOnDeviceEngine {
    private let config: OmniInferenceConfig
    private var vocabulary: [String: Int] = [:]
    private var reverseVocab: [Int: String] = [:]
    
    #if canImport(CoreML)
    private var coreMLModel: MLModel?
    #endif
    
    init(config: OmniInferenceConfig = OmniInferenceConfig()) {
        self.config = config
    }
    
    #if canImport(CoreML)
    func loadCoreMLModel(at url: URL) throws {
        let compiledURL = try MLModel.compileModel(at: url)
        let configuration = MLModelConfiguration()
        configuration.computeUnits = .all
        self.coreMLModel = try MLModel(contentsOf: compiledURL, configuration: configuration)
    }
    #endif
    
    func loadVocabulary(from url: URL) throws {
        let data = try Data(contentsOf: url)
        guard let vocab = try JSONSerialization.jsonObject(with: data) as? [String: Int] else {
            throw OmniError.invalidVocabulary
        }
        self.vocabulary = vocab
        self.reverseVocab = Dictionary(uniqueKeysWithValues: vocab.map { ($1, $0) })
    }
    
    func tokenize(_ text: String) -> [Int] {
        // Simple word-level tokenization (production would use BPE)
        return text.lowercased().split(separator: " ").compactMap { vocabulary[String($0)] }
    }
    
    func detokenize(_ ids: [Int]) -> String {
        return ids.compactMap { reverseVocab[$0] }.joined(separator: " ")
    }
    
    func generate(prompt: String) -> GenerationResult {
        let startTime = CFAbsoluteTimeGetCurrent()
        let inputIds = tokenize(prompt)
        var generatedIds: [Int] = inputIds
        var finishReason: GenerationResult.FinishReason = .maxTokens
        
        for _ in 0..<config.maxTokens {
            // Get next token logits (production: forward pass through model)
            var logits = OmniTensor.zeros(shape: [vocabulary.count])
            
            // Apply temperature
            if config.temperature > 0 {
                var temp = 1.0 / config.temperature
                vDSP_vsmul(logits.data, 1, &temp, &logits.data, 1, vDSP_Length(logits.count))
            }
            
            // Apply top-p sampling
            logits.softmax()
            let nextToken = sampleTopP(probs: logits.data, topP: config.topP)
            
            if config.stopTokenIds.contains(nextToken) {
                finishReason = .stop
                break
            }
            generatedIds.append(nextToken)
        }
        
        let latency = (CFAbsoluteTimeGetCurrent() - startTime) * 1000.0
        let newTokens = Array(generatedIds.dropFirst(inputIds.count))
        
        return GenerationResult(
            text: detokenize(newTokens),
            tokenIds: newTokens,
            tokensGenerated: newTokens.count,
            latencyMs: latency,
            finishReason: finishReason
        )
    }
    
    private func sampleTopP(probs: [Float], topP: Float) -> Int {
        let indexed = probs.enumerated().sorted { $0.element > $1.element }
        var cumProb: Float = 0.0
        var candidates: [(Int, Float)] = []
        
        for (idx, prob) in indexed {
            cumProb += prob
            candidates.append((idx, prob))
            if cumProb >= topP { break }
        }
        
        let total = candidates.reduce(0.0) { $0 + $1.1 }
        let r = Float.random(in: 0..<total)
        var running: Float = 0.0
        for (idx, prob) in candidates {
            running += prob
            if running >= r { return idx }
        }
        return candidates.last?.0 ?? 0
    }
}

// MARK: - Error Types
enum OmniError: Error {
    case invalidVocabulary
    case modelNotLoaded
    case inferenceFailure(String)
}
