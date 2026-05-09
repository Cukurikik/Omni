// OmniDatasetPipeline.cs — Dataset Pipeline Domain Service
// Inspired by: Bio-NER/FashionCLIP dataset management patterns
// Layer: Domain / C# Business Logic
//
// Data ingestion, validation, and transformation pipeline for
// multimodal training datasets with versioning and lineage tracking.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Text;

namespace Omni.Domain.Dataset
{
    public enum DatasetFormat
    {
        Parquet, CSV, JSONL, TFRecord, WebDataset, Arrow, HuggingFace
    }

    public enum SplitType { Train, Validation, Test }

    public enum QualityGrade { A, B, C, Rejected }

    public record DatasetVersion(
        string VersionId,
        int MajorVersion,
        int MinorVersion,
        DateTime CreatedAt,
        string Description,
        string ParentVersionId
    );

    public record DataSample(
        string SampleId,
        Dictionary<string, object> Features,
        SplitType Split,
        QualityGrade Grade,
        string SourceId
    );

    public record DatasetStats(
        long TotalSamples,
        long TrainSamples,
        long ValidationSamples,
        long TestSamples,
        Dictionary<QualityGrade, long> QualityDistribution,
        Dictionary<string, double> FeatureStats,
        double DataQualityScore
    );

    public record TransformRule(
        string Name,
        string FieldName,
        Func<object, object> Transform,
        Func<object, bool> Validation
    );

    public class DatasetPipeline
    {
        public string DatasetId { get; }
        public string Name { get; }
        public DatasetFormat Format { get; }

        private readonly List<DataSample> _samples = new();
        private readonly List<TransformRule> _transforms = new();
        private readonly List<DatasetVersion> _versions = new();
        private readonly Dictionary<string, string> _lineage = new();

        public IReadOnlyList<DataSample> Samples => _samples;
        public IReadOnlyList<DatasetVersion> Versions => _versions;

        public DatasetPipeline(string name, DatasetFormat format)
        {
            DatasetId = GenerateId(name);
            Name = name;
            Format = format;
            _versions.Add(new DatasetVersion(
                GenerateId("v0"), 0, 1, DateTime.UtcNow,
                "Initial version", ""
            ));
        }

        public void AddSamples(IEnumerable<DataSample> samples)
        {
            foreach (var sample in samples)
            {
                var validated = ValidateSample(sample);
                if (validated.Grade != QualityGrade.Rejected)
                {
                    _samples.Add(validated);
                    _lineage[validated.SampleId] = validated.SourceId;
                }
            }
        }

        public void AddTransform(TransformRule rule)
        {
            _transforms.Add(rule);
        }

        public List<DataSample> ApplyTransforms()
        {
            var transformed = new List<DataSample>();
            foreach (var sample in _samples)
            {
                var features = new Dictionary<string, object>(sample.Features);
                bool valid = true;

                foreach (var rule in _transforms)
                {
                    if (features.TryGetValue(rule.FieldName, out var value))
                    {
                        if (rule.Validation(value))
                        {
                            features[rule.FieldName] = rule.Transform(value);
                        }
                        else
                        {
                            valid = false;
                            break;
                        }
                    }
                }

                if (valid)
                {
                    transformed.Add(sample with { Features = features });
                }
            }
            return transformed;
        }

        public (List<DataSample> Train, List<DataSample> Val, List<DataSample> Test) Split(
            double trainRatio = 0.8, double valRatio = 0.1, int seed = 42)
        {
            var rng = new Random(seed);
            var shuffled = _samples.OrderBy(_ => rng.Next()).ToList();

            int trainEnd = (int)(shuffled.Count * trainRatio);
            int valEnd = trainEnd + (int)(shuffled.Count * valRatio);

            var train = shuffled.Take(trainEnd)
                .Select(s => s with { Split = SplitType.Train }).ToList();
            var val = shuffled.Skip(trainEnd).Take(valEnd - trainEnd)
                .Select(s => s with { Split = SplitType.Validation }).ToList();
            var test = shuffled.Skip(valEnd)
                .Select(s => s with { Split = SplitType.Test }).ToList();

            return (train, val, test);
        }

        public DatasetStats ComputeStats()
        {
            var qualityDist = _samples
                .GroupBy(s => s.Grade)
                .ToDictionary(g => g.Key, g => (long)g.Count());

            var numericFeatures = new Dictionary<string, List<double>>();
            foreach (var sample in _samples)
            {
                foreach (var kv in sample.Features)
                {
                    if (kv.Value is double d)
                    {
                        if (!numericFeatures.ContainsKey(kv.Key))
                            numericFeatures[kv.Key] = new List<double>();
                        numericFeatures[kv.Key].Add(d);
                    }
                }
            }

            var featureStats = new Dictionary<string, double>();
            foreach (var kv in numericFeatures)
            {
                featureStats[$"{kv.Key}_mean"] = kv.Value.Average();
                featureStats[$"{kv.Key}_std"] = StdDev(kv.Value);
                featureStats[$"{kv.Key}_min"] = kv.Value.Min();
                featureStats[$"{kv.Key}_max"] = kv.Value.Max();
            }

            double qualityScore = _samples.Count > 0
                ? (double)_samples.Count(s => s.Grade == QualityGrade.A) / _samples.Count
                : 0;

            return new DatasetStats(
                _samples.Count,
                _samples.Count(s => s.Split == SplitType.Train),
                _samples.Count(s => s.Split == SplitType.Validation),
                _samples.Count(s => s.Split == SplitType.Test),
                qualityDist,
                featureStats,
                qualityScore
            );
        }

        public DatasetVersion CreateVersion(string description)
        {
            var latest = _versions.Last();
            var version = new DatasetVersion(
                GenerateId($"v{latest.MajorVersion}.{latest.MinorVersion + 1}"),
                latest.MajorVersion,
                latest.MinorVersion + 1,
                DateTime.UtcNow,
                description,
                latest.VersionId
            );
            _versions.Add(version);
            return version;
        }

        public Dictionary<string, int> GetLabelDistribution(string labelField)
        {
            return _samples
                .Where(s => s.Features.ContainsKey(labelField))
                .GroupBy(s => s.Features[labelField]?.ToString() ?? "null")
                .ToDictionary(g => g.Key, g => g.Count());
        }

        private DataSample ValidateSample(DataSample sample)
        {
            if (sample.Features == null || sample.Features.Count == 0)
                return sample with { Grade = QualityGrade.Rejected };

            bool hasNulls = sample.Features.Values.Any(v => v == null);
            if (hasNulls)
                return sample with { Grade = QualityGrade.C };

            return sample;
        }

        private static double StdDev(List<double> values)
        {
            double mean = values.Average();
            double variance = values.Select(v => (v - mean) * (v - mean)).Sum()
                / Math.Max(values.Count - 1, 1);
            return Math.Sqrt(variance);
        }

        private static string GenerateId(string input)
        {
            using var sha = SHA256.Create();
            var hash = sha.ComputeHash(Encoding.UTF8.GetBytes(input + DateTime.UtcNow.Ticks));
            return Convert.ToHexString(hash)[..12].ToLower();
        }
    }
}
