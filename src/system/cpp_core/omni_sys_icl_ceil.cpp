#include <cstdint>
#include <cmath>

// OMNI System Kernel: K-Means centroid update
extern "C" {
        double compute(const double* cluster_pts, int32_t len) {
            double sum = 0.0;
            for(int i=0; i<len; i++) sum += cluster_pts[i];
            return len == 0 ? 0 : sum / len;
        }
}