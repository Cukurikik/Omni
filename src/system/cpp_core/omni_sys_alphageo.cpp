#include <cmath>

extern "C" {
    /// Compute Euclidean distance for geometry proof verification.
    double omni_sys_alphageo_distance(double x1, double y1, double x2, double y2) {
        double dx = x2 - x1, dy = y2 - y1;
        return std::sqrt(dx * dx + dy * dy);
    }

    /// Verify collinearity of three points via cross product.
    int omni_sys_alphageo_collinear(double x1, double y1, double x2, double y2, double x3, double y3) {
        double cross = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1);
        return std::fabs(cross) < 1e-9 ? 1 : 0;
    }
}
