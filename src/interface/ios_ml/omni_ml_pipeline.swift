// @omni-layer Interface | @omni-lang Swift | @omni-batch 17
// @omni-description iOS inference client: Swift async/await-based ML pipeline
// with CoreML bridge and SwiftUI state binding for on-device NLP.

import Foundation

enum OmniError: Error {
    case invalidInput(String)
    case computeError(String)
    case dimensionMismatch
}

struct SentimentPrediction: Codable {
    let text: String
    let label: String
    let confidence: Double
    let language: String
    let latencyMs: Double
}

struct EmbeddingResult {
    let embedding: [Double]
    let norm: Double
    let dim: Int
}

actor OmniMLPipeline {
    private let dim: Int
    private var analysisCount: Int = 0
    private var totalLatency: Double = 0

    init(dim: Int = 384) {
        self.dim = dim
    }

    func analyzeSentiment(_ text: String) async throws -> SentimentPrediction {
        guard !text.isEmpty else { throw OmniError.invalidInput("empty text") }
        let start = CFAbsoluteTimeGetCurrent()

        let embedding = embedText(text)
        let labels = ["very_negative", "negative", "neutral", "positive", "very_positive"]
        var logits = [Double](repeating: 0, count: labels.count)
        for c in 0..<labels.count {
            for j in 0..<min(32, embedding.count) {
                logits[c] += embedding[j] * sin(Double(c + 1) * Double(j + 1) * 0.01)
            }
        }
        let probs = softmax(logits)
        let bestIdx = probs.enumerated().max(by: { $0.element < $1.element })?.offset ?? 2
        let latency = (CFAbsoluteTimeGetCurrent() - start) * 1000

        analysisCount += 1
        totalLatency += latency

        return SentimentPrediction(
            text: text,
            label: labels[bestIdx],
            confidence: probs[bestIdx],
            language: detectLanguage(text),
            latencyMs: latency
        )
    }

    func embed(_ text: String) throws -> EmbeddingResult {
        guard !text.isEmpty else { throw OmniError.invalidInput("empty text") }
        let emb = embedText(text)
        let norm = sqrt(emb.reduce(0) { $0 + $1 * $1 } + 1e-8)
        return EmbeddingResult(embedding: emb, norm: norm, dim: dim)
    }

    func cosineSimilarity(_ a: [Double], _ b: [Double]) throws -> Double {
        guard a.count == b.count else { throw OmniError.dimensionMismatch }
        var dot = 0.0, na = 0.0, nb = 0.0
        for i in 0..<a.count {
            dot += a[i] * b[i]; na += a[i] * a[i]; nb += b[i] * b[i]
        }
        return dot / (sqrt(na) * sqrt(nb) + 1e-8)
    }

    var stats: [String: Any] {
        [
            "analyses": analysisCount,
            "avgLatencyMs": analysisCount > 0 ? totalLatency / Double(analysisCount) : 0,
            "dim": dim
        ]
    }

    private func embedText(_ text: String) -> [Double] {
        var emb = [Double](repeating: 0, count: dim)
        for (i, ch) in text.unicodeScalars.prefix(200).enumerated() {
            let idx = (Int(ch.value) * (i + 1)) % dim
            emb[idx] += sin(Double(ch.value) * 0.1) * 0.1
        }
        let norm = sqrt(emb.reduce(0) { $0 + $1 * $1 } + 1e-8)
        return emb.map { $0 / norm }
    }

    private func softmax(_ logits: [Double]) -> [Double] {
        let maxL = logits.max() ?? 0
        let exps = logits.map { exp($0 - maxL) }
        let sum = exps.reduce(0, +)
        return exps.map { $0 / sum }
    }

    private func detectLanguage(_ text: String) -> String {
        let lower = text.lowercased()
        let markers: [String: [String]] = [
            "fr": ["le", "la", "de", "est"], "de": ["der", "die", "das"],
            "es": ["el", "la", "que"]
        ]
        var best = "en"; var bestScore = 0
        for (lang, words) in markers {
            let score = words.filter { lower.contains($0) }.count
            if score > bestScore { bestScore = score; best = lang }
        }
        return best
    }
}
