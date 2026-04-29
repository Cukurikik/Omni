#include <cstdint>

extern "C" {
    // OMNI System Layer - Hard realtime PID math kernel
    double compute_pid_step(double kp, double ki, double kd, 
                            double setpoint, double measured, 
                            double* prev_error, double* integral, double dt) {
        if (dt <= 0.0 || !prev_error || !integral) return 0.0;
        
        double error = setpoint - measured;
        *integral += error * dt;
        double derivative = (error - *prev_error) / dt;
        *prev_error = error;
        
        return (kp * error) + (ki * *integral) + (kd * derivative);
    }
}
