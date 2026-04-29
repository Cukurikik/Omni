import Foundation

/// Omni INTERS Search Tuning (Swift)
/// Based on DaoD/INTERS
/// Unlocking Large Language Models in Search via Instruction Tuning

public enum INTERSError: Error {
    case emptyCorpus
    case invalidQuery
}

public struct OmniIntersSearch {
    
    public func tuneSearchWeights(query: String, corpusCount: Int) -> Result<Double, INTERSError> {
        guard !query.isEmpty else {
            return .failure(.invalidQuery)
        }
        guard corpusCount > 0 else {
            return .failure(.emptyCorpus)
        }
        
        // Deterministic instruction-based tuning factor calculation
        let baseWeight = Double(query.count) / Double(corpusCount)
        let tunedWeight = min(max(baseWeight * 1.5, 0.1), 1.0)
        
        return .success(tunedWeight)
    }
}
