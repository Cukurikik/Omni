// Omni Flora Optimizer Business (C#)
// Ref: BorealisAI/flora-opt — ICML 2024
namespace Omni.Business.Flora {
    public static class FloraOptimizerConfig {
        public static int ComputeProjectionDim(int modelDim, int compressionRatio = 16) {
            return System.Math.Max(modelDim / compressionRatio, 1);
        }
        public static double MemorySavingsRatio(int fullDim, int projDim) {
            return 1.0 - (double)projDim / fullDim;
        }
    }
}
