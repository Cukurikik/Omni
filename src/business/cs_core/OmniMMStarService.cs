// Omni MMStar VLM Scorer (C#)
// Ref: MMStar-Benchmark/MMStar — NeurIPS 2024
using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.MMStar
{
    public static class MMStarService
    {
        public static bool EvaluateVQA(string prediction, string answer)
            => prediction.Trim().ToUpper() == answer.Trim().ToUpper();

        public static bool DetectLeakage(string textOnlyResponse, string answer)
            => textOnlyResponse.Trim().ToUpper() == answer.Trim().ToUpper();

        public static Dictionary<string, double> AggregateByCapability(
            List<(string Capability, bool Correct)> results)
        {
            return results.GroupBy(r => r.Capability)
                          .ToDictionary(g => g.Key,
                                        g => Math.Round(g.Average(r => r.Correct ? 1.0 : 0.0), 4));
        }
    }
}
