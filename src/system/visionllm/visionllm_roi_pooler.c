/* VisionLLM — Region-of-Interest Feature Pooler
 * C kernel for extracting fixed-size features from variable bounding boxes */
#include <stdint.h>
#include <math.h>

#define MAX_ROIS 10000
#define MAX_CHANNELS 2048
#define MAX_POOL_SIZE 14

typedef struct { int is_ok; float value; const char* error; } OmniResult_f32;

typedef struct { float x1, y1, x2, y2; } BBox;

OmniResult_f32 roi_align_single(
    const float* feature_map, uint32_t fm_h, uint32_t fm_w, uint32_t channels,
    const BBox* roi, float spatial_scale
) {
    if (!feature_map || !roi) return (OmniResult_f32){0, 0, "Null pointer"};
    if (channels > MAX_CHANNELS) return (OmniResult_f32){0, 0, "Channels exceed 2048"};
    if (fm_h == 0 || fm_w == 0) return (OmniResult_f32){0, 0, "Zero feature map dims"};
    float rx1 = roi->x1 * spatial_scale;
    float ry1 = roi->y1 * spatial_scale;
    float rx2 = roi->x2 * spatial_scale;
    float ry2 = roi->y2 * spatial_scale;
    if (rx1 >= rx2 || ry1 >= ry2) return (OmniResult_f32){0, 0, "Invalid ROI dimensions"};
    float roi_w = rx2 - rx1;
    float roi_h = ry2 - ry1;
    float bin_w = roi_w / (float)MAX_POOL_SIZE;
    float bin_h = roi_h / (float)MAX_POOL_SIZE;
    float sum = 0.0f;
    uint32_t count = 0;
    for (int ph = 0; ph < MAX_POOL_SIZE; ph++) {
        for (int pw = 0; pw < MAX_POOL_SIZE; pw++) {
            float cy = ry1 + (ph + 0.5f) * bin_h;
            float cx = rx1 + (pw + 0.5f) * bin_w;
            int iy = (int)cy, ix = (int)cx;
            if (iy >= 0 && iy < (int)fm_h && ix >= 0 && ix < (int)fm_w) {
                sum += feature_map[iy * fm_w + ix];
                count++;
            }
        }
    }
    return (OmniResult_f32){1, count > 0 ? sum / count : 0.0f, NULL};
}
