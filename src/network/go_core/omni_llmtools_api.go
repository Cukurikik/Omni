// Omni LLM-Tools Memory API (Go)
package go_core
func InferenceMemoryGB(paramsB float64, bits int, kvTokens int, nLayers int) float64 {
	bpp := float64(bits) / 8; model := paramsB * 1e9 * bpp / 1e9
	kv := 2.0 * float64(kvTokens) * 32 * 128 * bpp * float64(nLayers) / 1e9
	return model + kv + model*0.1
}
func TrainingMemoryGB(paramsB float64, bits int) float64 {
	bpp := float64(bits) / 8; model := paramsB * 1e9 * bpp / 1e9
	return model*2 + paramsB*1e9*8/1e9 + model*0.5
}
