using System;

namespace Omni.Domain.Omninet
{
    public class OmninetConfig
    {
        public int SpatialDimensions { get; private set; }
        public int TemporalContextSize { get; private set; }
        public bool EnableCrossAttention { get; private set; }

        public OmninetConfig(int spatialDim, int temporalCtx, bool enableCross)
        {
            if (spatialDim <= 0) throw new ArgumentOutOfRangeException(nameof(spatialDim));
            if (temporalCtx <= 0) throw new ArgumentOutOfRangeException(nameof(temporalCtx));

            SpatialDimensions = spatialDim;
            TemporalContextSize = temporalCtx;
            EnableCrossAttention = enableCross;
        }

        public string GeneratePipelineToken()
        {
            return $"OMNI-NET-{SpatialDimensions}x{TemporalContextSize}-{(EnableCrossAttention ? "CA" : "SA")}-{Guid.NewGuid().ToString().Substring(0, 8)}";
        }
    }
}
