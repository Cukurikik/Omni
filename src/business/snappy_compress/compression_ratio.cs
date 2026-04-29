using System;

namespace Omni.Business.SnappyCompress
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class CompressionRatio
    {
        public OmniResult<bool> ShouldCompress(long uncompressed_size, long compressed_size)
        {
            if (uncompressed_size <= 0)
            {
                return new OmniResult<bool>(new ArgumentException("Uncompressed size must be positive"));
            }

            if (compressed_size <= 0)
            {
                return new OmniResult<bool>(new ArgumentException("Compressed size must be positive"));
            }

            // Snappy business rule: If compression doesn't yield at least 12.5% reduction (ratio < 0.875),
            // it is often better to store uncompressed to save decompression CPU cycles.
            double ratio = (double)compressed_size / uncompressed_size;
            
            bool is_worth_compressing = ratio <= 0.875;

            return new OmniResult<bool>(is_worth_compressing);
        }
    }
}
