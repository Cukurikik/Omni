#include <cmath>

extern "C" {
    /// Compute IoU between two bounding boxes [x1,y1,x2,y2].
    float omni_sys_anylabeling_iou(float ax1, float ay1, float ax2, float ay2,
                                    float bx1, float by1, float bx2, float by2) {
        float inter_x1 = (ax1 > bx1) ? ax1 : bx1;
        float inter_y1 = (ay1 > by1) ? ay1 : by1;
        float inter_x2 = (ax2 < bx2) ? ax2 : bx2;
        float inter_y2 = (ay2 < by2) ? ay2 : by2;
        float inter_w = (inter_x2 - inter_x1 > 0) ? inter_x2 - inter_x1 : 0;
        float inter_h = (inter_y2 - inter_y1 > 0) ? inter_y2 - inter_y1 : 0;
        float inter_area = inter_w * inter_h;
        float area_a = (ax2 - ax1) * (ay2 - ay1);
        float area_b = (bx2 - bx1) * (by2 - by1);
        float union_area = area_a + area_b - inter_area;
        return (union_area > 0) ? inter_area / union_area : 0.0f;
    }
}
