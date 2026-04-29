#include <cstdint>
#include <cmath>

// OMNI System Kernel: RPN simplified pop
extern "C" {
        double compute(const double* stack, int32_t len) {
            double res = 0.0;
            for(int i=0; i<len; i++) res += stack[i];
            return res;
        }
}