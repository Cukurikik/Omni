using System;

namespace Omni.Business.FifthDimensionTesseractStorage
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class NonEuclideanGc
    {
        public OmniResult<string> EvaluateGarbageCollection(double storage_usage_percentage, bool hyper_axis_aligned)
        {
            if (storage_usage_percentage < 0 || storage_usage_percentage > 100)
            {
                return new OmniResult<string>(new ArgumentException("Invalid storage percentage"));
            }

            // Infrastructure Business Logic: Non-Euclidean Garbage Collection
            // When deleting data in a 5D hypercube, standard 3D algorithms fail.
            // Fragments of deleted data can "hide" in orthogonal axes not visible to 3D space,
            // eventually causing the tesseract to bloat and rupture into 3D space.
            
            if (!hyper_axis_aligned)
            {
                return new OmniResult<string>("AXIS_MISALIGNMENT: Garbage collector cannot access the W or U axes. Deleted data fragments are leaking into the 4th and 5th dimensions. Re-align tesseract immediately.");
            }
            
            if (storage_usage_percentage > 99.0)
            {
                 return new OmniResult<string>("HYPER_VOLUME_CRITICAL: Tesseract storage nearly full. Risk of Euclidean space rupture. Initiate hyper-volume defragmentation.");
            }
            
            return new OmniResult<string>("GC_NOMINAL: Non-Euclidean garbage collection completing across all 5 spatial axes. Data cleanly purged from the multiverse.");
        }
    }
}
