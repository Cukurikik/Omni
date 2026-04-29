import Foundation
struct OmniResult<T> { let isOk: Bool; let value: T?; let error: String? }
struct PointCloudView {
    let maxPoints: Int = 1_000_000
    func renderStats(pointCount: Int, sampledCount: Int) -> OmniResult<[String: Any]> {
        guard pointCount > 0 else { return OmniResult(isOk: false, value: nil, error: "Empty cloud") }
        guard pointCount <= maxPoints else { return OmniResult(isOk: false, value: nil, error: "Points exceed 1M") }
        guard sampledCount <= pointCount else { return OmniResult(isOk: false, value: nil, error: "Sampled > total") }
        let ratio = Double(sampledCount) / Double(pointCount)
        let stats: [String: Any] = ["total": pointCount, "sampled": sampledCount, "ratio": ratio]
        return OmniResult(isOk: true, value: stats, error: nil)
    }
}
