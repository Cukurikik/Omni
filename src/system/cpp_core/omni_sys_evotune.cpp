extern "C" {
    void omni_sys_evotune_crossover(const float* p1, const float* p2, float* child, int size, int split_point) {
        if (!p1 || !p2 || !child || size <= 0) return;
        
        int sp = split_point;
        if (sp < 0) sp = 0;
        if (sp > size) sp = size;
        
        for (int i = 0; i < sp; ++i) {
            child[i] = p1[i];
        }
        for (int i = sp; i < size; ++i) {
            child[i] = p2[i];
        }
    }
}
