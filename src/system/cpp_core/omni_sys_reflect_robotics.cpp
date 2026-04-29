#include <cstdint>
#include <cmath>

// OMNI System Kernel: PID Controller Output
extern "C" {
        double compute(double kp, double ki, double kd, double error, double integral, double derivative) {
            return (kp * error) + (ki * integral) + (kd * derivative);
        }
}