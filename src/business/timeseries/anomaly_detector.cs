using System;
using System.Collections.Generic;
using Omni.Core.Result;

namespace Omni.Business.TimeSeries
{
    // OMNI BUSINESS LAYER: Time Series Anomaly Detector
    // Applies Z-Score based anomaly detection over rolling windows.

    public class AnomalyEvent
    {
        public int Index { get; set; }
        public double Value { get; set; }
        public double ZScore { get; set; }
        public bool IsSpike { get; set; }
    }

    public class AnomalyDetector
    {
        public OmniResult<List<AnomalyEvent>, string> DetectAnomalies(List<double> series, double zThreshold = 3.0)
        {
            try
            {
                var anomalies = new List<AnomalyEvent>();
                if (series.Count < 2) return OmniResult<List<AnomalyEvent>, string>.Ok(anomalies);

                double sum = 0;
                foreach (var val in series) sum += val;
                double mean = sum / series.Count;

                double sumSq = 0;
                foreach (var val in series) sumSq += Math.Pow(val - mean, 2);
                double stdDev = Math.Sqrt(sumSq / (series.Count - 1));

                if (stdDev == 0) return OmniResult<List<AnomalyEvent>, string>.Ok(anomalies);

                for (int i = 0; i < series.Count; i++)
                {
                    double zScore = (series[i] - mean) / stdDev;
                    if (Math.Abs(zScore) > zThreshold)
                    {
                        anomalies.Add(new AnomalyEvent
                        {
                            Index = i,
                            Value = series[i],
                            ZScore = zScore,
                            IsSpike = zScore > 0
                        });
                    }
                }

                return OmniResult<List<AnomalyEvent>, string>.Ok(anomalies);
            }
            catch (Exception ex)
            {
                return OmniResult<List<AnomalyEvent>, string>.Err($"Anomaly detection failed: {ex.Message}");
            }
        }
    }
}
