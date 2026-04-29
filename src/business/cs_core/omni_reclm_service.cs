// Omni RecLM Business Service (C#)
// Ref: HKUDS/RecLM — ACL2025
namespace Omni.Business.RecLM {
    public static class InstructionTuningService {
        public static int ValidateProfile(string userHistory, string itemMeta) {
            if (string.IsNullOrWhiteSpace(userHistory)) return -1;
            if (string.IsNullOrWhiteSpace(itemMeta)) return -2;
            return 0;
        }
        public static double PPOReward(int predictedRank, int gtRank, int maxRank = 100) {
            if (predictedRank <= gtRank) return 1.0 - (double)predictedRank / maxRank;
            return -0.5 * (predictedRank - gtRank) / (double)maxRank;
        }
    }
}
