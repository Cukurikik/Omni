// Omni EasyRec Recommendation Service (C#)
// Business Layer: Collaborative filtering business logic.
// Ref: HKUDS/EasyRec — EMNLP 2025
namespace Omni.Business.EasyRec {
    public readonly struct RecommendationRequest { public string UserId { get; init; } public int TopK { get; init; } }
    public readonly struct RecommendationResult { public string ItemId { get; init; } public double Score { get; init; } }
    public static class OmniEasyRecService {
        public static int ValidateRequest(RecommendationRequest req) {
            if (string.IsNullOrEmpty(req.UserId)) return -1;
            return System.Math.Clamp(req.TopK, 1, 100);
        }
    }
}
