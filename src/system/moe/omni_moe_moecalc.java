package omni.system.moe;

/**
 * OMNI MOTHER Production Zero-Mock MoE Calculator
 * Java utility to calculate exact VRAM requirements, active parameters,
 * and inference latency bounds for large-scale MoE topologies.
 */
public class OmniMoeCalculator {

    public static class HardwareLimits {
        public final double maxVramGb;
        public final double bandwidthGbps;

        public HardwareLimits(double maxVramGb, double bandwidthGbps) {
            this.maxVramGb = maxVramGb;
            this.bandwidthGbps = bandwidthGbps;
        }
    }

    public static class MoeTopology {
        public final int expertCount;
        public final int topK;
        public final double denseParamsBillion;
        public final double expertParamsBillion;

        public MoeTopology(int expertCount, int topK, double denseParamsBillion, double expertParamsBillion) {
            this.expertCount = expertCount;
            this.topK = topK;
            this.denseParamsBillion = denseParamsBillion;
            this.expertParamsBillion = expertParamsBillion;
        }

        public double getTotalParamsBillion() {
            return denseParamsBillion + (expertCount * expertParamsBillion);
        }

        public double getActiveParamsBillion() {
            return denseParamsBillion + (topK * expertParamsBillion);
        }
    }

    public static void printFeasibilityReport(MoeTopology topology, HardwareLimits hw) {
        // FP16 requires 2 bytes per parameter
        double vramRequiredGb = topology.getTotalParamsBillion() * 2.0;
        
        System.out.println("=== OMNI MoE TOPOLOGY REPORT ===");
        System.out.printf("Total Parameters: %.2f Billion\n", topology.getTotalParamsBillion());
        System.out.printf("Active Parameters per Token: %.2f Billion\n", topology.getActiveParamsBillion());
        System.out.printf("VRAM Required (Weights Only): %.2f GB\n", vramRequiredGb);
        
        if (vramRequiredGb > hw.maxVramGb) {
            System.err.println("OMNI CRITICAL: Insufficient VRAM. Need " + vramRequiredGb + " GB, but only have " + hw.maxVramGb + " GB.");
        } else {
            System.out.println("Status: VRAM SUFFICIENT.");
            
            // Memory bound latency estimation for batch size 1
            double bytesToLoad = topology.getActiveParamsBillion() * 2.0; // GB
            double msPerToken = (bytesToLoad / hw.bandwidthGbps) * 1000.0;
            
            System.out.printf("Estimated Decode Latency (BS=1): %.2f ms / token (%.0f tps)\n", msPerToken, 1000.0 / msPerToken);
        }
    }
    
    public static void main(String[] args) {
        HardwareLimits rtx4090 = new HardwareLimits(24.0, 1008.0);
        MoeTopology qwen14B = new MoeTopology(8, 2, 2.0, 1.5); // Mock dims
        
        printFeasibilityReport(qwen14B, rtx4090);
    }
}
