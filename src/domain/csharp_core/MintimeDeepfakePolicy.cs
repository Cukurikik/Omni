using System;

namespace Omni.Domain.Security
{
    public class MintimeDeepfakePolicy
    {
        public double Threshold { get; }

        public MintimeDeepfakePolicy(double threshold)
        {
            Threshold = threshold;
        }
    }
}
