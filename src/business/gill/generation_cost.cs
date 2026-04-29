using System;

namespace Omni.Gill
{
    public class OmniResult<T>
    {
        public T Value { get; set; }
        public string Error { get; set; }
        public bool IsOk { get; set; }
    }

    public class GenerationCost
    {
        public OmniResult<double> CalculateImageCost(int resolution, int steps)
        {
            if (resolution <= 0 || steps <= 0)
            {
                return new OmniResult<double> { Error = "Invalid parameters", IsOk = false };
            }
            
            // C# business rules for billing image generation based on resolution and diffusion steps
            double cost = (resolution * steps) * 0.0001;
            
            return new OmniResult<double> { Value = cost, IsOk = true };
        }
    }
}
