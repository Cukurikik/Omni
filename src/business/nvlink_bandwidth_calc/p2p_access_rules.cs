using System;

namespace Omni.Business.NvlinkBandwidthCalc
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class P2pAccessRules
    {
        public OmniResult<bool> IsP2pAccessAllowed(int gpu_source, int gpu_target, bool requires_pcie_hop)
        {
            if (gpu_source < 0 || gpu_target < 0)
            {
                return new OmniResult<bool>(new ArgumentException("GPU IDs must be valid"));
            }

            // NVLink Business Logic: Peer-to-Peer Access Verification
            // GPUs can only communicate directly (P2P) if they are connected via NVLink/NVSwitch.
            // If they must route through the host CPU's PCIe bus, it creates a massive bottleneck.
            
            if (requires_pcie_hop)
            {
                // Reject P2P access if it traverses PCIe. Fallback to staging through Host RAM.
                return new OmniResult<bool>(false);
            }
            
            return new OmniResult<bool>(true);
        }
    }
}
