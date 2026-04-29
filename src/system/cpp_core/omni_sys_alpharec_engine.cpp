#include <cstdint>
#include <cmath>

// OMNI System Kernel: Pearson correlation coefficient
extern "C" {
        double compute(const double* x, const double* y, int32_t len) {
            double sum_x = 0, sum_y = 0, sum_xy = 0, sum_x2 = 0, sum_y2 = 0;
            for(int i=0; i<len; i++) {
                sum_x += x[i]; sum_y += y[i];
                sum_xy += x[i]*y[i];
                sum_x2 += x[i]*x[i]; sum_y2 += y[i]*y[i];
            }
            double num = (len * sum_xy) - (sum_x * sum_y);
            double den = std::sqrt((len * sum_x2 - sum_x*sum_x) * (len * sum_y2 - sum_y*sum_y));
            return den == 0 ? 0 : num / den;
        }
}