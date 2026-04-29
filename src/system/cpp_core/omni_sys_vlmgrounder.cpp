#include <cmath>

extern "C" {
    float omni_sys_vlmgrounder_iou3d(const float* box_a, const float* box_b) {
        if (!box_a || !box_b) return 0.0f;
        // box format: x, y, z, w, h, d
        
        float xA = std::max(box_a[0], box_b[0]);
        float yA = std::max(box_a[1], box_b[1]);
        float zA = std::max(box_a[2], box_b[2]);
        
        float xB = std::min(box_a[0] + box_a[3], box_b[0] + box_b[3]);
        float yB = std::min(box_a[1] + box_a[4], box_b[1] + box_b[4]);
        float zB = std::min(box_a[2] + box_a[5], box_b[2] + box_b[5]);
        
        float inter_w = std::max(0.0f, xB - xA);
        float inter_h = std::max(0.0f, yB - yA);
        float inter_d = std::max(0.0f, zB - zA);
        
        float inter_vol = inter_w * inter_h * inter_d;
        float vol_a = box_a[3] * box_a[4] * box_a[5];
        float vol_b = box_b[3] * box_b[4] * box_b[5];
        
        float union_vol = vol_a + vol_b - inter_vol;
        if (union_vol <= 0.0f) return 0.0f;
        
        return inter_vol / union_vol;
    }
}
