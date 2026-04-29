using System;
using System.Collections.Generic;
using System.Linq;

// OMNI IMPLICIT: Recommendation Engine
// C# domain logic mapping users to items based on computed matrix factorization scores.
// Source: benfred/implicit

namespace Omni.Implicit
{
    public class RecommendationResult
    {
        public string ItemId { get; set; }
        public float Score { get; set; }
    }

    public class RecommendationEngine
    {
        // Mocked pre-computed factors representing the latent space
        private readonly Dictionary<string, float[]> _userFactors;
        private readonly Dictionary<string, float[]> _itemFactors;

        public RecommendationEngine()
        {
            _userFactors = new Dictionary<string, float[]>();
            _itemFactors = new Dictionary<string, float[]>();
        }

        public void LoadModel(Dictionary<string, float[]> users, Dictionary<string, float[]> items)
        {
            foreach (var kvp in users) _userFactors[kvp.Key] = kvp.Value;
            foreach (var kvp in items) _itemFactors[kvp.Key] = kvp.Value;
        }

        /// <summary>
        /// Generates Top-N recommendations for a given user using dot product of latent vectors.
        /// </summary>
        public List<RecommendationResult> Recommend(string userId, int n = 10, HashSet<string> filterItems = null)
        {
            if (!_userFactors.ContainsKey(userId))
            {
                return new List<RecommendationResult>(); // Unknown user
            }

            var uf = _userFactors[userId];
            var scores = new List<RecommendationResult>();

            foreach (var item in _itemFactors)
            {
                if (filterItems != null && filterItems.Contains(item.Key)) continue;

                var itf = item.Value;
                float dotProduct = 0;
                for (int i = 0; i < uf.Length; i++)
                {
                    dotProduct += uf[i] * itf[i];
                }

                scores.Add(new RecommendationResult { ItemId = item.Key, Score = dotProduct });
            }

            // Sort descending and take top N
            return scores.OrderByDescending(r => r.Score).Take(n).ToList();
        }
    }
}
