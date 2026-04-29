// Omni TIFA Faithfulness Service (C#)
using System; using System.Collections.Generic; using System.Linq;
namespace Omni.TIFA {
    public static class TIFAService {
        public static double ComputeScore(List<bool> answers) {
            if (!answers.Any()) return 0; return Math.Round((double)answers.Count(a => a) / answers.Count, 4);
        }
        public static Dictionary<string, double> ElementBreakdown(List<(string Type, bool Correct)> answers) {
            return answers.GroupBy(a => a.Type).ToDictionary(g => g.Key, g => Math.Round((double)g.Count(x => x.Correct) / g.Count(), 4));
        }
    }
}
