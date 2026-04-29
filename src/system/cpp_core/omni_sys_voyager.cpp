#include <cmath>

extern "C" {
    float omni_sys_voyager_biome_distance(float x1, float z1, float x2, float z2) {
        // 2D euclidean distance in block coordinates
        float dx = x2 - x1;
        float dz = z2 - z1;
        return std::sqrt(dx * dx + dz * dz);
    }
}
