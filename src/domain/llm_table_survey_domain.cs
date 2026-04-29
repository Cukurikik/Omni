using System;
using Omni.Domain.Monads;

namespace Omni.Business.LLMTableSurvey
{
    public class SurveyDomain
    {
        public Result<SurveyMetrics, Exception> ValidateSurvey(SurveyRequest request)
        {
            if (string.IsNullOrEmpty(request.SurveyId))
            {
                return Result<SurveyMetrics, Exception>.Err(new ArgumentException("Survey ID missing"));
            }
            var metrics = new SurveyMetrics { Verified = true, Score = 95.5 };
            return Result<SurveyMetrics, Exception>.Ok(metrics);
        }
    }
    
    public class SurveyRequest { public string SurveyId { get; set; } }
    public class SurveyMetrics { public bool Verified { get; set; } public double Score { get; set; } }
}
