// OmniModelDashboard.swift — Model Metrics Dashboard for Apple Platforms
// Inspired by: OMNI model serving monitoring requirements
// Layer: Interface / Swift
//
// SwiftUI-ready model performance monitoring with real-time
// latency histograms, throughput gauges, and error rate tracking.

import Foundation

public enum MetricType: String, Codable {
    case latency, throughput, errorRate, accuracy, memoryUsage, gpuUtilization
}

public struct MetricSample: Codable, Identifiable {
    public let id: UUID
    public let metricType: MetricType
    public let value: Double
    public let timestamp: Date
    public let modelName: String
    public let tags: [String: String]

    public init(metricType: MetricType, value: Double, modelName: String,
                tags: [String: String] = [:]) {
        self.id = UUID()
        self.metricType = metricType
        self.value = value
        self.timestamp = Date()
        self.modelName = modelName
        self.tags = tags
    }
}

public struct LatencyHistogram {
    private var buckets: [Double: Int]
    private let boundaries: [Double]
    private(set) var count: Int = 0
    private(set) var sum: Double = 0

    public init(boundaries: [Double] = [1, 5, 10, 25, 50, 100, 250, 500, 1000]) {
        self.boundaries = boundaries.sorted()
        self.buckets = Dictionary(uniqueKeysWithValues: boundaries.map { ($0, 0) })
    }

    public mutating func record(_ value: Double) {
        count += 1
        sum += value
        for boundary in boundaries {
            if value <= boundary {
                buckets[boundary, default: 0] += 1
            }
        }
    }

    public var mean: Double { count > 0 ? sum / Double(count) : 0 }

    public func percentile(_ p: Double) -> Double {
        let targetCount = Int(Double(count) * p)
        var cumulative = 0
        for boundary in boundaries {
            cumulative += buckets[boundary, default: 0]
            if cumulative >= targetCount {
                return boundary
            }
        }
        return boundaries.last ?? 0
    }

    public var p50: Double { percentile(0.5) }
    public var p95: Double { percentile(0.95) }
    public var p99: Double { percentile(0.99) }
}

public struct ThroughputGauge {
    private var windowSamples: [(timestamp: Date, count: Int)] = []
    private let windowDuration: TimeInterval

    public init(windowSeconds: TimeInterval = 60) {
        self.windowDuration = windowSeconds
    }

    public mutating func record(batchSize: Int = 1) {
        let now = Date()
        windowSamples.append((timestamp: now, count: batchSize))
        windowSamples.removeAll { now.timeIntervalSince($0.timestamp) > windowDuration }
    }

    public var requestsPerSecond: Double {
        guard windowSamples.count > 1,
              let first = windowSamples.first,
              let last = windowSamples.last else { return 0 }
        let duration = last.timestamp.timeIntervalSince(first.timestamp)
        guard duration > 0 else { return 0 }
        let total = windowSamples.reduce(0) { $0 + $1.count }
        return Double(total) / duration
    }
}

public struct ErrorTracker {
    private var errors: [(Date, String)] = []
    private var totalRequests: Int = 0
    private let maxHistory: Int

    public init(maxHistory: Int = 1000) {
        self.maxHistory = maxHistory
    }

    public mutating func recordSuccess() { totalRequests += 1 }

    public mutating func recordError(_ message: String) {
        totalRequests += 1
        errors.append((Date(), message))
        if errors.count > maxHistory {
            errors.removeFirst(errors.count - maxHistory)
        }
    }

    public var errorRate: Double {
        totalRequests > 0 ? Double(errors.count) / Double(totalRequests) : 0
    }

    public var recentErrors: [(Date, String)] {
        Array(errors.suffix(10))
    }
}

public class OmniModelDashboard: ObservableObject {
    @Published public private(set) var latencyHistograms: [String: LatencyHistogram] = [:]
    @Published public private(set) var throughputGauges: [String: ThroughputGauge] = [:]
    @Published public private(set) var errorTrackers: [String: ErrorTracker] = [:]
    @Published public private(set) var metricHistory: [MetricSample] = []

    private let maxHistorySize: Int
    private let queue = DispatchQueue(label: "omni.dashboard", qos: .utility)

    public init(maxHistorySize: Int = 10000) {
        self.maxHistorySize = maxHistorySize
    }

    public func recordInference(modelName: String, latencyMs: Double,
                                batchSize: Int = 1, success: Bool = true,
                                errorMessage: String? = nil) {
        queue.async { [weak self] in
            guard let self = self else { return }

            var hist = self.latencyHistograms[modelName] ?? LatencyHistogram()
            hist.record(latencyMs)
            self.latencyHistograms[modelName] = hist

            var gauge = self.throughputGauges[modelName] ?? ThroughputGauge()
            gauge.record(batchSize: batchSize)
            self.throughputGauges[modelName] = gauge

            var tracker = self.errorTrackers[modelName] ?? ErrorTracker()
            if success {
                tracker.recordSuccess()
            } else {
                tracker.recordError(errorMessage ?? "unknown error")
            }
            self.errorTrackers[modelName] = tracker

            let sample = MetricSample(
                metricType: .latency, value: latencyMs,
                modelName: modelName, tags: ["batch_size": "\(batchSize)"]
            )
            self.metricHistory.append(sample)
            if self.metricHistory.count > self.maxHistorySize {
                self.metricHistory.removeFirst(self.metricHistory.count - self.maxHistorySize)
            }
        }
    }

    public func getSummary(modelName: String) -> [String: Any] {
        var summary: [String: Any] = ["model": modelName]

        if let hist = latencyHistograms[modelName] {
            summary["latency_mean_ms"] = hist.mean
            summary["latency_p50_ms"] = hist.p50
            summary["latency_p95_ms"] = hist.p95
            summary["latency_p99_ms"] = hist.p99
            summary["total_inferences"] = hist.count
        }

        if let gauge = throughputGauges[modelName] {
            summary["throughput_rps"] = gauge.requestsPerSecond
        }

        if let tracker = errorTrackers[modelName] {
            summary["error_rate"] = tracker.errorRate
        }

        return summary
    }
}
