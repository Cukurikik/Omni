#include <cstdint>
extern "C" {
    float omni_sys_arxiv_times_h_index(const int* citations, int n) {
        if (!citations || n <= 0) return 0.0f;
        int h = 0;
        for (int i = 0; i < n; ++i) if (citations[i] >= i + 1) h = i + 1;
        return (float)h;
    }
}
