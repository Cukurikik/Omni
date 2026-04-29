#include <stdint.h>
#include <stddef.h>

typedef enum {
    AD_SUCCESS = 0,
    AD_ERR_NULL_POINTER = -1,
    AD_ERR_SENSOR_FAILURE = -2
} AD_Status;

typedef struct {
    float lidar_distance;
    float camera_confidence;
    float steering_angle;
} AD_Telemetry;

/*
 * Autonomous Driving GenAI stack layer. Zero-allocation bare metal logic.
 */
AD_Status omni_ad_compute_trajectory(const AD_Telemetry* telemetry, float* out_steering) {
    if (!telemetry || !out_steering) {
        return AD_ERR_NULL_POINTER;
    }
    
    if (telemetry->camera_confidence < 0.5f) {
        return AD_ERR_SENSOR_FAILURE;
    }
    
    // Deterministic fusion of lidar and camera
    float safety_factor = (telemetry->lidar_distance > 10.0f) ? 1.0f : (telemetry->lidar_distance / 10.0f);
    *out_steering = telemetry->steering_angle * safety_factor;
    
    return AD_SUCCESS;
}
