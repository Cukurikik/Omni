// Omni AgentReview Business (C#)
// Ref: Ahren09/AgentReview — EMNLP'24
namespace Omni.Business.AgentReview {
    public static class ReviewDecision {
        public static string Decide(double meanScore) {
            if (meanScore >= 6.0) return "accept";
            if (meanScore >= 4.5) return "borderline";
            return "reject";
        }
        public static double BiasVariance(double[] scores) {
            if (scores.Length < 2) return 0;
            double mean = 0; foreach (var s in scores) mean += s; mean /= scores.Length;
            double v = 0; foreach (var s in scores) v += (s - mean) * (s - mean);
            return v / scores.Length;
        }
    }
}
