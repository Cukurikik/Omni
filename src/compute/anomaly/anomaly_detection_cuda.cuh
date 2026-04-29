// OMNI Divine Memory Integration: Inspired by anomaly-detection-resources
// Compute Layer - CUDA header for defining boundaries on isolation forests

#ifndef OMNI_ANOMALY_CUDA_H
#define OMNI_ANOMALY_CUDA_H

#define MAX_TREES 1024
#define MAX_SAMPLES_PER_TREE 256

typedef struct {
    int code;
    const char* message;
} OmniError;

typedef struct {
    int is_ok;
    float score;
    OmniError error;
} OmniScoreResult;

// External C++ binding
extern "C" OmniScoreResult compute_isolation_score_cuda(float* d_data, int num_samples);

#endif // OMNI_ANOMALY_CUDA_H
