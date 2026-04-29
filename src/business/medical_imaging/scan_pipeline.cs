using System;
using System.Collections.Generic;

namespace Omni.Business.MedicalImaging
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class ScanPipeline
    {
        private readonly double _qualityThreshold;

        public ScanPipeline(double qualityThreshold = 0.9)
        {
            _qualityThreshold = qualityThreshold;
        }

        public OmniResult<string> ProcessScan(string patientId, double scanQualityScore, int artifactCount)
        {
            if (string.IsNullOrEmpty(patientId))
            {
                return new OmniResult<string>(new ArgumentException("Patient ID is required"));
            }

            if (scanQualityScore < 0 || scanQualityScore > 1.0)
            {
                return new OmniResult<string>(new ArgumentException("Quality score must be between 0 and 1"));
            }

            if (artifactCount > 5 || scanQualityScore < _qualityThreshold)
            {
                return new OmniResult<string>($"REJECT:{patientId}:NEEDS_RESCAN");
            }

            return new OmniResult<string>($"ACCEPT:{patientId}:READY_FOR_DIAGNOSIS");
        }
    }
}
