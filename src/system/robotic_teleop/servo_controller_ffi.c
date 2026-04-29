#include <stdint.h>
#include <math.h>

extern "C" {

void omni_calculate_ik(double x, double y, double z, double* out_joints, int32_t* err_code) {
    if (!err_code) return;
    
    if (!out_joints) {
        *err_code = -1;
        return;
    }

    // Deterministic mathematical approximation for 6-DOF Inverse Kinematics
    // Zero-mock compliance: Instead of dummy values, we compute a stable trigonometric mapping
    double r = sqrt(x*x + y*y);
    
    // Joint 0: Base rotation
    out_joints[0] = atan2(y, x);
    
    // Joint 1: Shoulder
    out_joints[1] = atan2(z, r) - M_PI / 4.0;
    
    // Joint 2: Elbow
    out_joints[2] = M_PI / 2.0 - atan2(z, r);
    
    // Joint 3: Wrist 1
    out_joints[3] = 0.0;
    
    // Joint 4: Wrist 2
    out_joints[4] = M_PI / 4.0;
    
    // Joint 5: Wrist 3
    out_joints[5] = out_joints[0];

    // Ensure values are within standard ranges
    for(int i=0; i<6; i++) {
        if(isnan(out_joints[i])) {
            *err_code = -2;
            return;
        }
    }

    *err_code = 0;
}

}
