#include <cstdint>

extern "C" {
    // VisionQA fast bounding box intersection area
    float visionqa_intersection_area(float a_x1, float a_y1, float a_x2, float a_y2,
                                     float b_x1, float b_y1, float b_x2, float b_y2) {
        float x_left = a_x1 > b_x1 ? a_x1 : b_x1;
        float y_top  = a_y1 > b_y1 ? a_y1 : b_y1;
        float x_right = a_x2 < b_x2 ? a_x2 : b_x2;
        float y_bottom = a_y2 < b_y2 ? a_y2 : b_y2;
        
        if (x_right < x_left || y_bottom < y_top) return 0.0f;
        return (x_right - x_left) * (y_bottom - y_top);
    }
}
