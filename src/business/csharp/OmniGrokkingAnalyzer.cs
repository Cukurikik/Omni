// OMNI Framework - C# Business Logic for Grokking Metrics Analysis
using System;
using System.Collections.Generic;
using System.Linq;

namespace OmniFramework.Business
{
    public class GrokkingMetrics
    {
        public int Epoch { get; set; }
        public double TrainLoss { get; set; }
        public double ValLoss { get; set; }
        public double TrainAccuracy { get; set; }
        public double ValAccuracy { get; set; }
    }

    public class OmniGrokkingAnalyzer
    {
        /// <summary>
        /// Analyzes grokking metrics to detect the "grokking point" where validation accuracy suddenly spikes
        /// after a period of overfitting.
        /// </summary>
        public int DetectGrokkingPoint(List<GrokkingMetrics> metrics, double accuracyThreshold = 0.95)
        {
            if (metrics == null || !metrics.Any())
                throw new ArgumentException("Metrics list cannot be empty.");

            var sortedMetrics = metrics.OrderBy(m => m.Epoch).ToList();
            
            for (int i = 0; i < sortedMetrics.Count; i++)
            {
                var metric = sortedMetrics[i];
                // Grokking occurs when train acc is high, but val acc suddenly jumps
                if (metric.TrainAccuracy > 0.99 && metric.ValAccuracy >= accuracyThreshold)
                {
                    return metric.Epoch;
                }
            }
            
            return -1; // Grokking point not found
        }
    }
}
