// Omni LoRA Quantizer (C#)
// Business Layer: 8-bit/4-bit LoRA adapter management for LLaMA.
// Ref: serp-ai/LLaMA-8bit-LoRA — LoRA training with quantization.
namespace Omni.Business.LoRA {
    public readonly struct LoRAConfig { public int Rank { get; init; } public float Alpha { get; init; } public int Bits { get; init; } }
    public static class OmniLoRAManager {
        public static double ComputeScalingFactor(LoRAConfig cfg) {
            if (cfg.Rank <= 0) return 0;
            return System.Math.Round(cfg.Alpha / cfg.Rank, 8);
        }
        public static long EstimateParamCount(int hiddenSize, int rank) {
            return 2L * hiddenSize * rank;
        }
    }
}
