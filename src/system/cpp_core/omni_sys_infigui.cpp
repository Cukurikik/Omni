#include <cmath>

extern "C" {
    struct GUIElement {
        int id;
        int parent_id;
        float x, y;
    };

    float omni_sys_infigui_distance(GUIElement a, GUIElement b) {
        float dx = a.x - b.x;
        float dy = a.y - b.y;
        float spatial_dist = std::sqrt(dx*dx + dy*dy);
        
        float tree_dist = (a.parent_id == b.parent_id) ? 1.0f : 5.0f;
        
        return spatial_dist + tree_dist;
    }
}
