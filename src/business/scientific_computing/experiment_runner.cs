using System;

namespace Omni.Business.ScientificComputing
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class ExperimentRunner
    {
        private readonly double _resourceLimitGb;

        public ExperimentRunner(double resourceLimitGb = 16.0)
        {
            _resourceLimitGb = resourceLimitGb;
        }

        public OmniResult<string> AllocateExperiment(string experimentId, int matrixDimension)
        {
            if (matrixDimension <= 0)
                return new OmniResult<string>(new ArgumentException("Matrix dimension must be > 0"));

            // Float64 takes 8 bytes. NxN matrix.
            double memoryRequiredGb = ((double)matrixDimension * matrixDimension * 8.0) / (1024 * 1024 * 1024);

            if (memoryRequiredGb > _resourceLimitGb)
            {
                return new OmniResult<string>(new OutOfMemoryException($"Experiment {experimentId} requires {memoryRequiredGb:F2}GB, exceeding limit of {_resourceLimitGb}GB"));
            }

            return new OmniResult<string>($"ALLOCATED:{experimentId}:{memoryRequiredGb:F4}GB");
        }
    }
}
