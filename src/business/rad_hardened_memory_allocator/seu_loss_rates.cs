using System;

namespace Omni.Business.RadHardenedMemoryAllocator
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class SeuLossRates
    {
        public OmniResult<bool> IsScrubRateAcceptable(int bit_flips_detected_per_hour, int max_acceptable_flips)
        {
            if (bit_flips_detected_per_hour < 0 || max_acceptable_flips <= 0)
            {
                return new OmniResult<bool>(new ArgumentException("Rates must be positive"));
            }

            // Radiation Tolerant Business Logic: Single Event Upset (SEU) Tracking
            // If the spacecraft enters the Van Allen belts or is hit by a Solar Flare,
            // the background memory scrubber will suddenly detect thousands of bit-flips.
            // If it exceeds the hardware ECC correction capacity, we must shut down non-critical systems.
            
            if (bit_flips_detected_per_hour > max_acceptable_flips)
            {
                return new OmniResult<bool>(false); // Unacceptable, trigger safe mode
            }
            
            return new OmniResult<bool>(true); // Nominal, scrubber is keeping up
        }
    }
}
