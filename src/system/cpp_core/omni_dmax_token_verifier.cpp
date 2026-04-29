// Omni DMax Parallel Token Verifier (C++)
// Ref: czg1225/DMax — Apache-2.0
#include <cmath>
#include <cstddef>
struct DMaxResult { int accepted; int proposed; float acceptance_rate; };
DMaxResult omni_verify_tokens(const int* proposed, const int* verified, int n) {
    DMaxResult r = {0, n, 0.0f};
    for (int i = 0; i < n; i++) {
        if (proposed[i] == verified[i]) r.accepted++;
        else break;
    }
    r.acceptance_rate = (float)r.accepted / (n > 0 ? n : 1);
    return r;
}
float omni_dmax_schedule(int step, int total, int base) {
    float progress = (float)step / (total > 0 ? total : 1);
    if (progress < 0.3f) return (float)(base * 2 < 16 ? base * 2 : 16);
    if (progress < 0.7f) return (float)base;
    return (float)(base / 2 > 1 ? base / 2 : 1);
}
