#include <cstdint>
extern "C" {
    int omni_sys_all_in_rag_reciprocal_rank(const int* retrieved, int n, int target_id) {
        if (!retrieved || n <= 0) return 0;
        for (int i = 0; i < n; ++i) {
            if (retrieved[i] == target_id) return i + 1;
        }
        return 0;
    }
    float omni_sys_all_in_rag_ndcg(const float* relevances, int n) {
        if (!relevances || n <= 0) return 0.0f;
        float dcg = 0, idcg = 0;
        for (int i = 0; i < n; ++i) {
            float disc = 1.0f / std::log2((float)(i + 2));
            dcg += relevances[i] * disc;
            idcg += (1.0f) * disc;
        }
        return idcg > 0 ? dcg / idcg : 0.0f;
    }
}
