using System;
using System.Collections.Generic;

namespace Omni.Business.FinFact
{
    public class Result<T, E>
    {
        public bool IsSuccess { get; }
        public T Value { get; }
        public E Error { get; }
        private Result(bool isSuccess, T value, E error) { IsSuccess = isSuccess; Value = value; Error = error; }
        public static Result<T, E> Success(T value) => new Result<T, E>(true, value, default!);
        public static Result<T, E> Failure(E error) => new Result<T, E>(false, default!, error);
    }

    public class Evidence
    {
        public string SourceUrl { get; set; } = string.Empty;
        public string Snippet { get; set; } = string.Empty;
        public double RelevanceScore { get; set; }
    }

    public class VerificationResult
    {
        public string Claim { get; set; } = string.Empty;
        public bool IsSupported { get; set; }
        public double Confidence { get; set; }
        public List<Evidence> SupportingEvidence { get; set; } = new List<Evidence>();
        public List<Evidence> RefutingEvidence { get; set; } = new List<Evidence>();
    }

    public class FactVerifier
    {
        public Result<VerificationResult, string> Verify(string claim, List<Evidence> retrievedEvidence)
        {
            if (string.IsNullOrWhiteSpace(claim)) return Result<VerificationResult, string>.Failure("Claim cannot be empty");
            if (retrievedEvidence == null) return Result<VerificationResult, string>.Failure("Evidence list cannot be null");

            var result = new VerificationResult { Claim = claim };
            double totalSupport = 0;
            double totalRefute = 0;

            foreach (var ev in retrievedEvidence)
            {
                // In production, this uses an NLI model. Here we mock the logic structurally for the engine.
                if (ev.RelevanceScore > 0.8)
                {
                    // Simulated sentiment/stance detection mapping
                    bool supports = ev.Snippet.Contains("increased", StringComparison.OrdinalIgnoreCase) || 
                                    ev.Snippet.Contains("reported", StringComparison.OrdinalIgnoreCase);
                    
                    if (supports)
                    {
                        result.SupportingEvidence.Add(ev);
                        totalSupport += ev.RelevanceScore;
                    }
                    else
                    {
                        result.RefutingEvidence.Add(ev);
                        totalRefute += ev.RelevanceScore;
                    }
                }
            }

            result.IsSupported = totalSupport > totalRefute;
            double totalScore = totalSupport + totalRefute;
            result.Confidence = totalScore > 0 ? Math.Max(totalSupport, totalRefute) / totalScore : 0;

            return Result<VerificationResult, string>.Success(result);
        }
    }
}
