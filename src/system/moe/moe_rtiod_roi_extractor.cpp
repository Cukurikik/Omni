// moe_rtiod_roi_extractor.cpp — System Layer: RTIOD ROI Extractor
// C++ implementation for optimizing Region of Interest (ROI) pooling in visual MoEs.

#include <vector>
#include <cmath>

namespace omni {
namespace system {
namespace rtiod {

class ROIPooler {
public:
    static void pool_region(const float* feature_map, int width, int height, 
                            float roi_xmin, float roi_ymin, float roi_xmax, float roi_ymax,
                            int pool_w, int pool_h, float* out_pooled) {
        
        // Zero-mock: calculate bin sizes
        float bin_w = (roi_xmax - roi_xmin) / pool_w;
        float bin_h = (roi_ymax - roi_ymin) / pool_h;
        
        for (int ph = 0; ph < pool_h; ++ph) {
            for (int pw = 0; pw < pool_w; ++pw) {
                int hstart = static_cast<int>(std::floor(roi_ymin + ph * bin_h));
                int wstart = static_cast<int>(std::floor(roi_xmin + pw * bin_w));
                int hend = static_cast<int>(std::ceil(roi_ymin + (ph + 1) * bin_h));
                int wend = static_cast<int>(std::ceil(roi_xmin + (pw + 1) * bin_w));
                
                hstart = std::max(0, std::min(hstart, height));
                hend = std::max(0, std::min(hend, height));
                wstart = std::max(0, std::min(wstart, width));
                wend = std::max(0, std::min(wend, width));

                float max_val = -1e9f;
                for (int h = hstart; h < hend; ++h) {
                    for (int w = wstart; w < wend; ++w) {
                        float val = feature_map[h * width + w];
                        if (val > max_val) max_val = val;
                    }
                }
                out_pooled[ph * pool_w + pw] = max_val;
            }
        }
    }
};

} // namespace rtiod
} // namespace system
} // namespace omni
