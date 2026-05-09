// OmniModelCompare.cs — Model Comparison Domain Service
// Inspired by: FashionCLIP + textsum evaluation patterns
// Layer: Domain / C# Business Logic
//
// DDD aggregate for A/B model comparison with statistical significance testing,
// experiment tracking, and production traffic splitting.

using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.Domain.ModelComparison
{
    public enum ExperimentStatus
    {
        Draft,
        Running,
        Paused,
        Completed,
        Cancelled
    }

    public enum TrafficSplitStrategy
    {
        EqualSplit,
        WeightedRandom,
        CanaryRollout,
        MultiArmedBandit
    }

    public record ModelVariant(
        string ModelId,
        string ModelName,
        string Version,
        double TrafficWeight,
        Dictionary<string, double> Metrics
    );

    public record EvaluationSample(
        string SampleId,
        string VariantId,
        Dictionary<string, double> Scores,
        double LatencyMs,
        DateTime Timestamp
    );

    public record StatisticalTestResult(
        string TestName,
        double PValue,
        double EffectSize,
        double ConfidenceInterval95Lower,
        double ConfidenceInterval95Upper,
        bool IsSignificant,
        string Summary
    );

    public class ModelExperiment
    {
        public string ExperimentId { get; }
        public string Name { get; }
        public string Description { get; }
        public ExperimentStatus Status { get; private set; }
        public TrafficSplitStrategy Strategy { get; }
        public DateTime CreatedAt { get; }
        public DateTime? StartedAt { get; private set; }
        public DateTime? CompletedAt { get; private set; }
        public int MinSamplesPerVariant { get; }
        public double SignificanceLevel { get; }

        private readonly Dictionary<string, ModelVariant> _variants;
        private readonly List<EvaluationSample> _samples;
        private readonly Random _rng;

        public IReadOnlyDictionary<string, ModelVariant> Variants => _variants;
        public IReadOnlyList<EvaluationSample> Samples => _samples;

        public ModelExperiment(
            string name,
            string description,
            TrafficSplitStrategy strategy,
            int minSamplesPerVariant = 1000,
            double significanceLevel = 0.05)
        {
            ExperimentId = Guid.NewGuid().ToString("N")[..12];
            Name = name ?? throw new ArgumentNullException(nameof(name));
            Description = description ?? "";
            Strategy = strategy;
            Status = ExperimentStatus.Draft;
            CreatedAt = DateTime.UtcNow;
            MinSamplesPerVariant = minSamplesPerVariant;
            SignificanceLevel = significanceLevel;
            _variants = new Dictionary<string, ModelVariant>();
            _samples = new List<EvaluationSample>();
            _rng = new Random(42);
        }

        public void AddVariant(ModelVariant variant)
        {
            if (Status != ExperimentStatus.Draft)
                throw new InvalidOperationException("Cannot add variants to a running experiment");

            if (_variants.ContainsKey(variant.ModelId))
                throw new ArgumentException($"Variant {variant.ModelId} already exists");

            _variants[variant.ModelId] = variant;
        }

        public void Start()
        {
            if (_variants.Count < 2)
                throw new InvalidOperationException("Need at least 2 variants for comparison");

            NormalizeTrafficWeights();
            Status = ExperimentStatus.Running;
            StartedAt = DateTime.UtcNow;
        }

        public string RouteRequest()
        {
            if (Status != ExperimentStatus.Running)
                throw new InvalidOperationException("Experiment is not running");

            switch (Strategy)
            {
                case TrafficSplitStrategy.EqualSplit:
                    return RouteEqualSplit();
                case TrafficSplitStrategy.WeightedRandom:
                    return RouteWeightedRandom();
                case TrafficSplitStrategy.CanaryRollout:
                    return RouteCanary();
                case TrafficSplitStrategy.MultiArmedBandit:
                    return RouteThompsonSampling();
                default:
                    return _variants.Keys.First();
            }
        }

        public void RecordSample(EvaluationSample sample)
        {
            if (!_variants.ContainsKey(sample.VariantId))
                throw new ArgumentException($"Unknown variant: {sample.VariantId}");

            _samples.Add(sample);

            if (HasSufficientSamples())
            {
                var result = RunSignificanceTest("accuracy");
                if (result.IsSignificant)
                {
                    Status = ExperimentStatus.Completed;
                    CompletedAt = DateTime.UtcNow;
                }
            }
        }

        public bool HasSufficientSamples()
        {
            return _variants.All(v =>
                _samples.Count(s => s.VariantId == v.Key) >= MinSamplesPerVariant);
        }

        public StatisticalTestResult RunSignificanceTest(string metricName)
        {
            var variantIds = _variants.Keys.ToList();
            if (variantIds.Count != 2)
                throw new InvalidOperationException("Statistical test requires exactly 2 variants");

            var samplesA = _samples
                .Where(s => s.VariantId == variantIds[0] && s.Scores.ContainsKey(metricName))
                .Select(s => s.Scores[metricName])
                .ToList();

            var samplesB = _samples
                .Where(s => s.VariantId == variantIds[1] && s.Scores.ContainsKey(metricName))
                .Select(s => s.Scores[metricName])
                .ToList();

            if (samplesA.Count < 2 || samplesB.Count < 2)
            {
                return new StatisticalTestResult(
                    "Welch's t-test", 1.0, 0.0, 0.0, 0.0, false,
                    "Insufficient samples for statistical testing"
                );
            }

            // Welch's t-test
            double meanA = samplesA.Average();
            double meanB = samplesB.Average();
            double varA = samplesA.Select(x => (x - meanA) * (x - meanA)).Sum() / (samplesA.Count - 1);
            double varB = samplesB.Select(x => (x - meanB) * (x - meanB)).Sum() / (samplesB.Count - 1);

            double seA = varA / samplesA.Count;
            double seB = varB / samplesB.Count;
            double se = Math.Sqrt(seA + seB);

            double tStat = se > 1e-10 ? (meanA - meanB) / se : 0;
            double effectSize = se > 1e-10 ? Math.Abs(meanA - meanB) / Math.Sqrt((varA + varB) / 2) : 0;

            // Approximate p-value using normal distribution (valid for large n)
            double pValue = 2 * (1 - NormalCDF(Math.Abs(tStat)));

            double ci95 = 1.96 * se;
            double diff = meanA - meanB;

            return new StatisticalTestResult(
                "Welch's t-test",
                pValue,
                effectSize,
                diff - ci95,
                diff + ci95,
                pValue < SignificanceLevel,
                $"Model A ({variantIds[0]}): μ={meanA:F4}, Model B ({variantIds[1]}): μ={meanB:F4}, " +
                $"Effect size: {effectSize:F4}, p={pValue:F6}"
            );
        }

        public Dictionary<string, Dictionary<string, double>> GetMetricsSummary()
        {
            var summary = new Dictionary<string, Dictionary<string, double>>();

            foreach (var variantId in _variants.Keys)
            {
                var variantSamples = _samples.Where(s => s.VariantId == variantId).ToList();
                var metrics = new Dictionary<string, double>
                {
                    ["sample_count"] = variantSamples.Count,
                    ["avg_latency_ms"] = variantSamples.Count > 0
                        ? variantSamples.Average(s => s.LatencyMs) : 0,
                    ["p95_latency_ms"] = variantSamples.Count > 0
                        ? Percentile(variantSamples.Select(s => s.LatencyMs).ToList(), 0.95) : 0,
                };

                var allMetricNames = variantSamples
                    .SelectMany(s => s.Scores.Keys)
                    .Distinct();

                foreach (var metric in allMetricNames)
                {
                    var values = variantSamples
                        .Where(s => s.Scores.ContainsKey(metric))
                        .Select(s => s.Scores[metric])
                        .ToList();

                    if (values.Count > 0)
                    {
                        metrics[$"avg_{metric}"] = values.Average();
                        metrics[$"std_{metric}"] = StdDev(values);
                    }
                }

                summary[variantId] = metrics;
            }

            return summary;
        }

        // Routing strategies
        private string RouteEqualSplit()
        {
            var keys = _variants.Keys.ToList();
            return keys[_rng.Next(keys.Count)];
        }

        private string RouteWeightedRandom()
        {
            double r = _rng.NextDouble();
            double cumulative = 0;
            foreach (var v in _variants.Values)
            {
                cumulative += v.TrafficWeight;
                if (r <= cumulative) return v.ModelId;
            }
            return _variants.Keys.Last();
        }

        private string RouteCanary()
        {
            // Route 90% to first variant, 10% to second
            var keys = _variants.Keys.ToList();
            return _rng.NextDouble() < 0.9 ? keys[0] : keys[^1];
        }

        private string RouteThompsonSampling()
        {
            // Simplified Thompson Sampling for A/B testing
            var keys = _variants.Keys.ToList();
            double bestScore = double.MinValue;
            string bestVariant = keys[0];

            foreach (var key in keys)
            {
                var scores = _samples
                    .Where(s => s.VariantId == key && s.Scores.ContainsKey("accuracy"))
                    .Select(s => s.Scores["accuracy"])
                    .ToList();

                double alpha = scores.Count(s => s >= 0.5) + 1;
                double beta = scores.Count(s => s < 0.5) + 1;

                // Sample from Beta distribution (approximation)
                double sample = SampleBeta(alpha, beta);
                if (sample > bestScore)
                {
                    bestScore = sample;
                    bestVariant = key;
                }
            }

            return bestVariant;
        }

        private void NormalizeTrafficWeights()
        {
            double total = _variants.Values.Sum(v => v.TrafficWeight);
            if (total <= 0) total = _variants.Count;

            var normalized = new Dictionary<string, ModelVariant>();
            foreach (var kvp in _variants)
            {
                normalized[kvp.Key] = kvp.Value with { TrafficWeight = kvp.Value.TrafficWeight / total };
            }
            _variants.Clear();
            foreach (var kvp in normalized)
            {
                _variants[kvp.Key] = kvp.Value;
            }
        }

        // Statistical helpers
        private static double NormalCDF(double x)
        {
            return 0.5 * (1.0 + Erf(x / Math.Sqrt(2.0)));
        }

        private static double Erf(double x)
        {
            double t = 1.0 / (1.0 + 0.3275911 * Math.Abs(x));
            double poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 +
                t * (-1.453152027 + t * 1.061405429))));
            double result = 1.0 - poly * Math.Exp(-x * x);
            return x >= 0 ? result : -result;
        }

        private static double Percentile(List<double> values, double p)
        {
            var sorted = values.OrderBy(v => v).ToList();
            int idx = (int)Math.Ceiling(p * sorted.Count) - 1;
            return sorted[Math.Max(0, Math.Min(idx, sorted.Count - 1))];
        }

        private static double StdDev(List<double> values)
        {
            double mean = values.Average();
            double variance = values.Select(v => (v - mean) * (v - mean)).Sum() / Math.Max(values.Count - 1, 1);
            return Math.Sqrt(variance);
        }

        private double SampleBeta(double alpha, double beta)
        {
            double x = SampleGamma(alpha);
            double y = SampleGamma(beta);
            return x / (x + y);
        }

        private double SampleGamma(double shape)
        {
            // Marsaglia and Tsang's method
            if (shape < 1) return SampleGamma(shape + 1) * Math.Pow(_rng.NextDouble(), 1.0 / shape);

            double d = shape - 1.0 / 3.0;
            double c = 1.0 / Math.Sqrt(9.0 * d);

            while (true)
            {
                double x, v;
                do
                {
                    x = NextGaussian();
                    v = 1.0 + c * x;
                } while (v <= 0);

                v = v * v * v;
                double u = _rng.NextDouble();

                if (u < 1.0 - 0.0331 * x * x * x * x) return d * v;
                if (Math.Log(u) < 0.5 * x * x + d * (1.0 - v + Math.Log(v))) return d * v;
            }
        }

        private double NextGaussian()
        {
            double u1 = 1.0 - _rng.NextDouble();
            double u2 = _rng.NextDouble();
            return Math.Sqrt(-2.0 * Math.Log(u1)) * Math.Cos(2.0 * Math.PI * u2);
        }
    }
}
