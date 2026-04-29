using System;

namespace Omni.Semester13.Batch08.AVLicensing
{
    public class AVLicenseError : Exception
    {
        public AVLicenseError(string msg) : base(msg) {}
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
    /// OMNI Engine: av-license-contract
    /// Business rules for evaluating audio-visual generation synchronization penalties.
    /// </summary>
    public class AVLicensingEngine
    {
        private readonly double _penaltyPerMsDrift;

        public AVLicensingEngine(double penaltyPerMsDrift = 1.25)
        {
            _penaltyPerMsDrift = penaltyPerMsDrift;
        }

        public Result<double> EvaluateSyncPenalty(double driftMs)
        {
            try
            {
                if (driftMs < 0.0)
                    return new Result<double>(new AVLicenseError("Drift absolute magnitude mathematically required"));

                // Business logic: If drift exceeds 50ms, it's noticeable, penalty kicks in.
                double penalty = 0.0;
                if (driftMs > 50.0) {
                     penalty = (driftMs - 50.0) * _penaltyPerMsDrift;
                }

                return new Result<double>(penalty);
            }
            catch (Exception ex)
            {
                return new Result<double>(new AVLicenseError($"License penalty mapping failed: {ex.Message}"));
            }
        }
    }
}
