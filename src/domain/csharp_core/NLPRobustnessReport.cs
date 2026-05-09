using System;
using System.Collections.Generic;

namespace Omni.Domain.NLP
{
    public class NLPRobustnessReport
    {
        public Guid ReportId { get; private set; }
        public string ModelIdentifier { get; private set; }
        public DateTime GeneratedAt { get; private set; }
        public int TotalProcessedQueries { get; private set; }
        public int OutOfDistributionCount { get; private set; }
        public double AverageConfidence { get; private set; }

        public NLPRobustnessReport(string modelIdentifier, int totalQueries, int oodCount, double avgConfidence)
        {
            if (string.IsNullOrWhiteSpace(modelIdentifier)) throw new ArgumentException("Model ID required");
            if (totalQueries < 0 || oodCount < 0) throw new ArgumentOutOfRangeException("Counts cannot be negative");

            ReportId = Guid.NewGuid();
            ModelIdentifier = modelIdentifier;
            GeneratedAt = DateTime.UtcNow;
            TotalProcessedQueries = totalQueries;
            OutOfDistributionCount = oodCount;
            AverageConfidence = avgConfidence;
        }

        public double GetOODPercentage()
        {
            if (TotalProcessedQueries == 0) return 0.0;
            return (double)OutOfDistributionCount / TotalProcessedQueries * 100.0;
        }

        public bool IsModelDegrading(double thresholdPercentage = 15.0)
        {
            return GetOODPercentage() > thresholdPercentage;
        }
    }
}
