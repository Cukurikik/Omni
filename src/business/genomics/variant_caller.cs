using System;
using System.Collections.Generic;

namespace Omni.Business.Genomics
{
    public class Result<T, E>
    {
        public bool IsSuccess { get; }
        public T Value { get; }
        public E Error { get; }

        private Result(bool isSuccess, T value, E error)
        {
            IsSuccess = isSuccess;
            Value = value;
            Error = error;
        }

        public static Result<T, E> Ok(T value) => new Result<T, E>(true, value, default);
        public static Result<T, E> Err(E error) => new Result<T, E>(false, default, error);
    }

    public class Variant
    {
        public string Chromosome { get; set; }
        public int Position { get; set; }
        public char Reference { get; set; }
        public char Alternate { get; set; }
        public double QualityScore { get; set; }
    }

    public class VariantCaller
    {
        private readonly double _qualityThreshold;

        public VariantCaller(double qualityThreshold = 30.0)
        {
            _qualityThreshold = qualityThreshold;
        }

        public Result<List<Variant>, string> CallVariants(string refSequence, List<string> readAlignments, int startPosition = 1)
        {
            if (string.IsNullOrEmpty(refSequence) || readAlignments == null || readAlignments.Count == 0)
            {
                return Result<List<Variant>, string>.Err("Invalid reference or read alignments");
            }

            var variants = new List<Variant>();
            int seqLen = refSequence.Length;

            try
            {
                // Simplified pileup logic
                for (int i = 0; i < seqLen; i++)
                {
                    char refBase = refSequence[i];
                    var baseCounts = new Dictionary<char, int> { { 'A', 0 }, { 'C', 0 }, { 'G', 0 }, { 'T', 0 }, { '-', 0 } };

                    foreach (var read in readAlignments)
                    {
                        if (i < read.Length)
                        {
                            char readBase = read[i];
                            if (baseCounts.ContainsKey(readBase))
                                baseCounts[readBase]++;
                        }
                    }

                    // Find most common non-reference base
                    char maxAlt = '-';
                    int maxCount = 0;
                    foreach (var kvp in baseCounts)
                    {
                        if (kvp.Key != refBase && kvp.Key != '-' && kvp.Value > maxCount)
                        {
                            maxAlt = kvp.Key;
                            maxCount = kvp.Value;
                        }
                    }

                    // Naive probability score (Phred-like)
                    double totalCoverage = readAlignments.Count;
                    double altFrequency = maxCount / totalCoverage;
                    
                    if (altFrequency > 0.2) // At least 20% reads show variant
                    {
                        // Simulated quality score based on frequency
                        double quality = -10 * Math.Log10(1.0 - altFrequency + 0.0001); 
                        
                        if (quality >= _qualityThreshold)
                        {
                            variants.Add(new Variant
                            {
                                Chromosome = "chr1", // Simplified
                                Position = startPosition + i,
                                Reference = refBase,
                                Alternate = maxAlt,
                                QualityScore = Math.Round(quality, 2)
                            });
                        }
                    }
                }

                return Result<List<Variant>, string>.Ok(variants);
            }
            catch (Exception ex)
            {
                return Result<List<Variant>, string>.Err($"Variant calling failed: {ex.Message}");
            }
        }
    }
}
