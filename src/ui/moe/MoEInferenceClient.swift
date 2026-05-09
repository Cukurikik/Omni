// MoEInferenceClient.swift — Swift MoE Inference Client
// Layer: UI / Interface — MoE Mobile Client (Swift/Apple)
//
// Type-safe Swift client for MoE model inference on Apple platforms.
// Uses async/await, Codable for serialization, and structured
// concurrency for parallel expert queries.

import Foundation

// MARK: - Data Types

public enum MoEClientError: Error, CustomStringConvertible {
    case networkError(String)
    case decodingError(String)
    case serverError(Int, String)
    case timeout
    case invalidConfiguration(String)

    public var description: String {
        switch self {
        case .networkError(let msg): return "Network error: \(msg)"
        case .decodingError(let msg): return "Decoding error: \(msg)"
        case .serverError(let code, let msg): return "Server error \(code): \(msg)"
        case .timeout: return "Request timed out"
        case .invalidConfiguration(let msg): return "Invalid config: \(msg)"
        }
    }
}

public struct InferenceRequest: Codable {
    public let requestId: String
    public let inputIds: [Int64]
    public let maxTokens: Int
    public let temperature: Double
    public let topK: Int
    public let topP: Double
    public let stream: Bool

    enum CodingKeys: String, CodingKey {
        case requestId = "request_id"
        case inputIds = "input_ids"
        case maxTokens = "max_tokens"
        case temperature, topK = "top_k", topP = "top_p", stream
    }

    public init(
        inputIds: [Int64],
        maxTokens: Int = 128,
        temperature: Double = 1.0,
        topK: Int = 50,
        topP: Double = 0.9,
        stream: Bool = false
    ) {
        self.requestId = UUID().uuidString
        self.inputIds = inputIds
        self.maxTokens = maxTokens
        self.temperature = temperature
        self.topK = topK
        self.topP = topP
        self.stream = stream
    }
}

public struct InferenceResponse: Codable {
    public let requestId: String
    public let outputIds: [Int64]
    public let expertUtilization: [Double]
    public let latencyMs: Double
    public let tokensPerSec: Double

    enum CodingKeys: String, CodingKey {
        case requestId = "request_id"
        case outputIds = "output_ids"
        case expertUtilization = "expert_utilization"
        case latencyMs = "latency_ms"
        case tokensPerSec = "tokens_per_sec"
    }
}

public struct HealthResponse: Codable {
    public let status: String
    public let healthyShards: Int
    public let totalShards: Int
    public let activeRequests: Int

    enum CodingKeys: String, CodingKey {
        case status
        case healthyShards = "healthy_shards"
        case totalShards = "total_shards"
        case activeRequests = "active_requests"
    }
}

public struct ExpertShard: Codable, Identifiable {
    public var id: Int { shardId }
    public let shardId: Int
    public let expertRange: [Int]
    public let host: String
    public let port: Int
    public let isHealthy: Bool
    public let loadFactor: Double

    enum CodingKeys: String, CodingKey {
        case shardId = "shard_id"
        case expertRange = "expert_range"
        case host, port
        case isHealthy = "is_healthy"
        case loadFactor = "load_factor"
    }
}

// MARK: - Result Type (Monadic Error Handling)

public enum Result<Success, Failure: Error> {
    case success(Success)
    case failure(Failure)

    public var value: Success? {
        if case .success(let v) = self { return v }
        return nil
    }

    public var error: Failure? {
        if case .failure(let e) = self { return e }
        return nil
    }

    public func map<T>(_ transform: (Success) -> T) -> Result<T, Failure> {
        switch self {
        case .success(let v): return .success(transform(v))
        case .failure(let e): return .failure(e)
        }
    }

    public func flatMap<T>(_ transform: (Success) -> Result<T, Failure>) -> Result<T, Failure> {
        switch self {
        case .success(let v): return transform(v)
        case .failure(let e): return .failure(e)
        }
    }
}

// MARK: - Client

public actor MoEInferenceClient {
    private let baseURL: URL
    private let session: URLSession
    private var metricsHistory: [MetricsSnapshot] = []
    private let maxHistorySize = 500

    public struct MetricsSnapshot {
        public let timestamp: Date
        public let latencyMs: Double
        public let tokensPerSec: Double
        public let expertUtilization: [Double]
        public let loadBalanceScore: Double
    }

    public init(baseURL: String, timeoutSeconds: TimeInterval = 30) {
        self.baseURL = URL(string: baseURL)!
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = timeoutSeconds
        config.timeoutIntervalForResource = timeoutSeconds * 2
        self.session = URLSession(configuration: config)
    }

    /// Run inference on the MoE model.
    public func infer(_ request: InferenceRequest) async -> Result<InferenceResponse, MoEClientError> {
        let result: Result<InferenceResponse, MoEClientError> = await post(path: "/v1/inference", body: request)
        if case .success(let response) = result {
            let snapshot = MetricsSnapshot(
                timestamp: Date(),
                latencyMs: response.latencyMs,
                tokensPerSec: response.tokensPerSec,
                expertUtilization: response.expertUtilization,
                loadBalanceScore: computeLoadBalance(response.expertUtilization)
            )
            metricsHistory.append(snapshot)
            if metricsHistory.count > maxHistorySize {
                metricsHistory.removeFirst()
            }
        }
        return result
    }

    /// Check gateway health.
    public func health() async -> Result<HealthResponse, MoEClientError> {
        return await get(path: "/v1/health")
    }

    /// Get shard information.
    public func shards() async -> Result<[ExpertShard], MoEClientError> {
        return await get(path: "/v1/shards")
    }

    /// Get metrics history.
    public func getMetricsHistory() -> [MetricsSnapshot] {
        return metricsHistory
    }

    // MARK: - Private Helpers

    private func get<T: Codable>(path: String) async -> Result<T, MoEClientError> {
        let url = baseURL.appendingPathComponent(path)
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        return await execute(request)
    }

    private func post<B: Codable, T: Codable>(path: String, body: B) async -> Result<T, MoEClientError> {
        let url = baseURL.appendingPathComponent(path)
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        do {
            request.httpBody = try JSONEncoder().encode(body)
        } catch {
            return .failure(.decodingError("Failed to encode request: \(error)"))
        }
        return await execute(request)
    }

    private func execute<T: Codable>(_ request: URLRequest) async -> Result<T, MoEClientError> {
        do {
            let (data, response) = try await session.data(for: request)
            guard let httpResponse = response as? HTTPURLResponse else {
                return .failure(.networkError("Invalid response type"))
            }
            guard (200...299).contains(httpResponse.statusCode) else {
                let body = String(data: data, encoding: .utf8) ?? "unknown"
                return .failure(.serverError(httpResponse.statusCode, body))
            }
            let decoded = try JSONDecoder().decode(T.self, from: data)
            return .success(decoded)
        } catch is URLError {
            return .failure(.timeout)
        } catch let error as DecodingError {
            return .failure(.decodingError("\(error)"))
        } catch {
            return .failure(.networkError("\(error)"))
        }
    }

    private func computeLoadBalance(_ utilization: [Double]) -> Double {
        guard !utilization.isEmpty else { return 0 }
        let mean = utilization.reduce(0, +) / Double(utilization.count)
        let variance = utilization.map { ($0 - mean) * ($0 - mean) }.reduce(0, +) / Double(utilization.count)
        let cv = sqrt(variance) / max(mean, 1e-8)
        return max(0, 1.0 - cv)
    }
}
