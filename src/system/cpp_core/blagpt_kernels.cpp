extern "C" {
    void blagpt_fast_gelu(float* data, int size) {
        for(int i = 0; i < size; ++i) {
            float x = data[i];
            data[i] = 0.5f * x * (1.0f + std::tanh(0.79788456f * (x + 0.044715f * x * x * x)));
        }
    }
}
