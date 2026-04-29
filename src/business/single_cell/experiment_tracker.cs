using System;
using System.Collections.Generic;

namespace Omni.Business.SingleCell
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class ExperimentTracker
    {
        private readonly Dictionary<string, string> _experiments;

        public ExperimentTracker()
        {
            _experiments = new Dictionary<string, string>();
        }

        public OmniResult<string> RecordBatch(string batchId, int cellCount, string targetOrgan)
        {
            if (cellCount <= 0)
                return new OmniResult<string>(new ArgumentException("Cell count must be > 0"));
                
            if (string.IsNullOrEmpty(targetOrgan))
                return new OmniResult<string>(new ArgumentException("Target organ cannot be empty"));

            var status = cellCount > 10000 ? "HIGH_THROUGHPUT" : "STANDARD";
            _experiments[batchId] = $"{targetOrgan}:{status}";
            
            return new OmniResult<string>($"Recorded {batchId} as {status}");
        }

        public OmniResult<string> GetBatchStatus(string batchId)
        {
            if (_experiments.TryGetValue(batchId, out var status))
            {
                return new OmniResult<string>(status);
            }
            return new OmniResult<string>(new KeyNotFoundException($"Batch {batchId} not found"));
        }
    }
}
