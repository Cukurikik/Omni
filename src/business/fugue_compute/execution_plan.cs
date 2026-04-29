using System;
using System.Collections.Generic;

namespace Omni.Business.FugueCompute
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class ExecutionPlan
    {
        public int MaxWorkers { get; }
        public int MemoryLimitGB { get; }

        public ExecutionPlan(int maxWorkers = 100, int memoryLimitGB = 512)
        {
            MaxWorkers = maxWorkers;
            MemoryLimitGB = memoryLimitGB;
        }

        public OmniResult<int> CalculateOptimalPartitions(long dataSizeMB)
        {
            if (dataSizeMB <= 0)
            {
                return new OmniResult<int>(new ArgumentException("Data size must be positive"));
            }

            // Business logic: Aim for ~128MB per partition (Hadoop/Spark standard)
            int targetPartitionSize = 128;
            int estimatedPartitions = (int)Math.Ceiling((double)dataSizeMB / targetPartitionSize);

            // Constraint: Do not exceed MaxWorkers * 4 to prevent task thrashing
            int maxAllowedPartitions = MaxWorkers * 4;

            int optimalPartitions = Math.Min(estimatedPartitions, maxAllowedPartitions);
            
            // Ensure at least 1 partition
            optimalPartitions = Math.Max(1, optimalPartitions);

            return new OmniResult<int>(optimalPartitions);
        }
    }
}
