using System.Collections.Generic;
using System.Linq;

namespace Omni.Business.Snorkel
{
    public class DataProgramming
    {
        // Applies multiple Labeling Functions (LFs) to a dataset and aggregates
        // mathematically to create probabilistic labels via Majority Vote (Baseline).
        public static List<int> ApplyMajorityVote(List<List<int>> lfOutputs)
        {
            var aggregatedLabels = new List<int>();
            
            foreach (var row in lfOutputs)
            {
                var votes = row.Where(l => l != -1); // -1 is abstain
                if (!votes.Any()) 
                {
                    aggregatedLabels.Add(-1);
                    continue;
                }

                // Group by label and pick max
                var majority = votes.GroupBy(v => v)
                                    .OrderByDescending(g => g.Count())
                                    .First().Key;
                aggregatedLabels.Add(majority);
            }
            
            return aggregatedLabels;
        }
    }
}
