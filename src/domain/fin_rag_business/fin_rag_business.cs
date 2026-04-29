using System;

namespace Omni.Semester13.Batch09.FinRAGBusiness
{
    public class FinRAGBizError : Exception
    {
        public FinRAGBizError(string msg) : base(msg) {}
    }

    public class Result<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public Result(T value) { Value = value; }
        public Result(Exception error) { Error = error; }

        public T Unwrap() {
            if (!IsOk) throw Error;
            return Value;
        }
    }

    /// <summary>
    /// OMNI Engine: finrag-business
    /// Business rules for evaluating acceptable hallucination boundaries in strict corporate RAG.
    /// </summary>
    public class FinRAGBusinessEngine
    {
        private readonly double _maxFinancialCitationDeviation;

        public FinRAGBusinessEngine(double maxDeviation = 0.01) // 1%
        {
            _maxFinancialCitationDeviation = maxDeviation;
        }

        public Result<bool> ValidateCorporateReportAccuracy(double citationDelta)
        {
            try
            {
                if (citationDelta < 0.0)
                    return new Result<bool>(new FinRAGBizError("Citation delta mathematically impossible as absolute negative"));

                // Logic: In PIF / Corporate reports, hallucinating a financial figure by > 1% is catastrophic business failure.
                bool isValid = citationDelta <= _maxFinancialCitationDeviation;

                return new Result<bool>(isValid);
            }
            catch (Exception ex)
            {
                return new Result<bool>(new FinRAGBizError($"Business mapping failed: {ex.Message}"));
            }
        }
    }
}
