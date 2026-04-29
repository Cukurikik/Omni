#include <cstdint>
#include <cmath>

// OMNI System Kernel: FedAvg Weight
extern "C" {
        double compute(const double* local_weights, const int32_t* data_sizes, int32_t len, int32_t total_data) {
            double avg = 0.0;
            if (total_data == 0) return 0.0;
            for(int i=0; i<len; i++) {
                avg += local_weights[i] * ((double)data_sizes[i] / total_data);
            }
            return avg;
        }
}