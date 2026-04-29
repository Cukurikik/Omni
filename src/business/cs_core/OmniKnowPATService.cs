// Omni KnowPAT Alignment Service (C#)
using System; using System.Collections.Generic; using System.Linq;
namespace Omni.KnowPAT {
    public static class KnowPATService {
        public static double DPOLoss(double chosenLogprob, double rejectedLogprob, double beta = 0.1) {
            double diff = beta * (chosenLogprob - rejectedLogprob);
            return -Math.Log(1.0 / (1.0 + Math.Exp(-diff)) + 1e-10);
        }
        public static double KnowledgeReward(string answer, List<string> facts) {
            var tokens = new HashSet<string>(answer.ToLower().Split(' '));
            int covered = facts.Count(f => f.ToLower().Split(' ').Any(t => tokens.Contains(t)));
            return Math.Round((double)covered / Math.Max(facts.Count, 1), 4);
        }
    }
}
