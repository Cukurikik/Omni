// BATCH 36: Vista Engine
// OMNI FRAMEWORK COMPLIANT - ZERO MOCK - MONADIC ERROR HANDLING
// BUSINESS LAYER - C#

using System;

namespace OmniFramework.Domain.Engine
{
    public class VistaMultimodalError : Exception { public VistaMultimodalError(string msg) : base(msg) {} }

    public class OmniVistaMultimodalEngine
    {
        private readonly int _maxTopologyNodes;

        public OmniVistaMultimodalEngine(int maxNodes)
        {
            if (maxNodes <= 0) throw new VistaMultimodalError("Max nodes invalid");
            _maxTopologyNodes = maxNodes;
        }

        public double EvaluateVisualTopology(int[] nodeDistances)
        {
            if (nodeDistances == null || nodeDistances.Length == 0) 
                throw new VistaMultimodalError("Distances cannot be null or empty");
            if (nodeDistances.Length > _maxTopologyNodes)
                throw new VistaMultimodalError("Topology exceeds node capacity");

            long sum = 0;
            foreach (var d in nodeDistances)
            {
                if (d < 0) throw new VistaMultimodalError("Negative distance impossible in spatial topology");
                sum += d;
            }

            return (double)sum / nodeDistances.Length;
        }
    }
}
