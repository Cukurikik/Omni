using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.Business.Finance
{
    // OMNI C# Service for Warren Buffet NLP Analysis
    public class OmniFinancialAnalyzer
    {
        private readonly Dictionary<string, double> _sentimentLexicon;

        public OmniFinancialAnalyzer()
        {
            // Loaded from DB in production
            _sentimentLexicon = new Dictionary<string, double>
            {
                { "growth", 1.2 }, { "value", 0.8 }, { "moat", 2.0 },
                { "risk", -1.5 }, { "loss", -2.0 }, { "inflation", -1.0 }
            };
        }

        public double ComputeTextPolarity(string document)
        {
            var words = document.ToLower().Split(new[] { ' ', '.', ',' }, StringSplitOptions.RemoveEmptyEntries);
            double score = 0;
            
            foreach (var word in words)
            {
                if (_sentimentLexicon.TryGetValue(word, out double weight))
                {
                    score += weight;
                }
            }
            
            return words.Length > 0 ? score / words.Length : 0;
        }
    }
}
