using System;

namespace Omni.Business.SyntheticPhotosynthesisReactor
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class CarbonCapture
    {
        public OmniResult<string> EvaluateAtmosphericDrawdown(double atmospheric_co2_ppm, double reactor_throughput_tons_per_day)
        {
            if (atmospheric_co2_ppm < 0 || reactor_throughput_tons_per_day < 0)
            {
                return new OmniResult<string>(new ArgumentException("Invalid atmospheric metrics"));
            }

            // Ecological Engineering Business Logic: Carbon Capture Scaling
            // To reverse climate change, we must scale synthetic photosynthesis to draw down
            // gigatons of CO2. If we drop below 150ppm, plant life on Earth will starve.
            
            if (atmospheric_co2_ppm < 180.0)
            {
                return new OmniResult<string>("ECOLOGICAL_THREAT_DETECTED: CO2 dropping below 180ppm. Natural flora starvation risk. Throttle down artificial reactors immediately.");
            }
            
            if (atmospheric_co2_ppm > 450.0 && reactor_throughput_tons_per_day < 1e6)
            {
                 return new OmniResult<string>("INSUFFICIENT_SCALE: CO2 exceeds safe limits. Current reactor throughput insufficient to halt thermal runaway. Increase global reactor deployment.");
            }
            
            return new OmniResult<string>("BIOSPHERE_STABLE: Artificial carbon cycle balanced. CO2 levels nominal.");
        }
    }
}
