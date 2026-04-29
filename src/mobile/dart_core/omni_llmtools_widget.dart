// Omni LLM-Tools Calculator Widget (Dart)
class LLMMemory {
  final double modelGb; final double kvGb; final double totalGb;
  LLMMemory({required this.modelGb, required this.kvGb, required this.totalGb});
}
class OmniLLMToolsWidget {
  static LLMMemory inferenceMemory(double paramsB, {int bits = 16, int kvTokens = 2048, int nLayers = 32}) {
    double bpp = bits / 8; double model = paramsB * 1e9 * bpp / 1e9;
    double kv = 2 * kvTokens * 32 * 128 * bpp * nLayers / 1e9;
    return LLMMemory(modelGb: model, kvGb: kv, totalGb: model + kv + model * 0.1);
  }
  static double quantSavingsGb(double paramsB, int origBits, int targetBits) =>
    paramsB * 1e9 * (origBits - targetBits) / 8 / 1e9;
}
