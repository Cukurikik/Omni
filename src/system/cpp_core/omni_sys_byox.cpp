extern "C" {
    void omni_sys_byox_gradient_step(const float* x, const float* y, float* w, float* b, int n, float lr) {
        if (n <= 0 || !x || !y || !w || !b) return;
        
        float dw = 0.0f;
        float db = 0.0f;
        
        for (int i = 0; i < n; ++i) {
            float pred = (*w) * x[i] + (*b);
            float diff = pred - y[i];
            dw += diff * x[i];
            db += diff;
        }
        
        *w -= lr * (2.0f / n) * dw;
        *b -= lr * (2.0f / n) * db;
    }
}
