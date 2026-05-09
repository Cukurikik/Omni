//=============================================================================
// OMNI DOMAIN LAYER — SENTIMENT AGGREGATE (C#)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: C# DDD Aggregate for storing and validating Sentiment Analysis 
//              results derived from BERT models.
//=============================================================================

using System;
using OmniBridge.Domain.Types;

namespace Omni.Domain.NLP
{
    // OMNI IDIOM: cs::domain
    public class SentimentRecord
    {
        public string TextId { get; private set; }
        public string OriginalText { get; private set; }
        public float PositiveScore { get; private set; }
        public float NeutralScore { get; private set; }
        public float NegativeScore { get; private set; }
        public SentimentCategory DominantCategory { get; private set; }
        public DateTime AnalyzedAt { get; private set; }

        public SentimentRecord(string textId, string text)
        {
            TextId = textId;
            OriginalText = text;
            AnalyzedAt = DateTime.UtcNow;
            DominantCategory = SentimentCategory.Unknown;
        }

        public MonadicResult<bool> ApplyBertResults(float pos, float neu, float neg)
        {
            if (pos < 0 || pos > 1 || neu < 0 || neu > 1 || neg < 0 || neg > 1)
            {
                return MonadicResult<bool>.Fail("Scores must be between 0.0 and 1.0");
            }

            // Margin of error validation for probability sum
            float sum = pos + neu + neg;
            if (Math.Abs(sum - 1.0f) > 0.01f)
            {
                return MonadicResult<bool>.Fail("Scores must sum to approximately 1.0");
            }

            PositiveScore = pos;
            NeutralScore = neu;
            NegativeScore = neg;

            if (pos > neu && pos > neg) DominantCategory = SentimentCategory.Positive;
            else if (neg > pos && neg > neu) DominantCategory = SentimentCategory.Negative;
            else DominantCategory = SentimentCategory.Neutral;

            return MonadicResult<bool>.Ok(true);
        }
    }

    public enum SentimentCategory
    {
        Positive,
        Neutral,
        Negative,
        Unknown
    }
}
