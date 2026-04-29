// Omni GUNDAM Data Quality Service (C#)
using System; using System.Collections.Generic; using System.Linq;
namespace Omni.GUNDAM {
    public static class GUNDAMService {
        public static double QualityScore(string text) {
            int words = text.Split(' ').Length; int unique = new HashSet<string>(text.ToLower().Split(' ')).Count;
            double diversity = (double)unique / Math.Max(words, 1);
            double length = Math.Min(words / 50.0, 1.0);
            return Math.Round((diversity + length) / 2, 4);
        }
        public static List<(string Text, double Score)> Prioritize(List<string> samples, int topK = 100) {
            return samples.Select(s => (s, QualityScore(s))).OrderByDescending(x => x.Item2).Take(topK).ToList();
        }
    }
}
