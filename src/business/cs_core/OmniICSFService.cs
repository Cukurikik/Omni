// Omni ICSFSurvey Self-Correction Service (C#)
using System; using System.Collections.Generic; using System.Linq;
namespace Omni.ICSF {
    public static class ICSFService {
        public static (string Winner, double Confidence) SelfConsistencyVote(List<string> answers) {
            var freq = answers.GroupBy(a => a).ToDictionary(g => g.Key, g => g.Count());
            var winner = freq.OrderByDescending(kv => kv.Value).First();
            return (winner.Key, Math.Round((double)winner.Value / answers.Count, 4));
        }
        public static double InternalConsistency(List<string> responses) {
            if (responses.Count < 2) return 1.0;
            var tokenSets = responses.Select(r => new HashSet<string>(r.ToLower().Split(' '))).ToList();
            double total = 0; int pairs = 0;
            for (int i = 0; i < tokenSets.Count; i++)
                for (int j = i+1; j < tokenSets.Count; j++) {
                    var inter = tokenSets[i].Intersect(tokenSets[j]).Count();
                    var union = tokenSets[i].Union(tokenSets[j]).Count();
                    total += (double)inter / Math.Max(union, 1); pairs++;
                }
            return Math.Round(total / Math.Max(pairs, 1), 4);
        }
    }
}
