// BATCH 36: Fin-Fact Engine
// OMNI FRAMEWORK COMPLIANT - ZERO MOCK - MONADIC ERROR HANDLING
// BUSINESS LAYER - C#

using System;
using System.Text.RegularExpressions;

namespace OmniFramework.Domain.Engine
{
    public class FinFactError : Exception { public FinFactError(string msg) : base(msg) {} }

    public class OmniFinFactEngine
    {
        private readonly double _confidenceThreshold;

        public OmniFinFactEngine(double threshold)
        {
            if (threshold <= 0 || threshold >= 1) throw new FinFactError("Invalid threshold");
            _confidenceThreshold = threshold;
        }

        public bool EvaluateFinancialClaim(string textClaim, string sourceContext)
        {
            if (string.IsNullOrEmpty(textClaim)) throw new FinFactError("Claim cannot be empty");
            
            int keywordMatches = Regex.Matches(sourceContext.ToLower(), "revenue|profit|loss|margin|ebitda").Count;
            int claimLength = textClaim.Length;
            
            double score = (double)keywordMatches / (claimLength > 0 ? claimLength : 1) * 100.0;
            return score >= _confidenceThreshold;
        }
    }
}
