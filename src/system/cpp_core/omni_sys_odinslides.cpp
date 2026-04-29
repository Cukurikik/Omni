#include <vector>
#include <string>
#include <stdexcept>
#include <algorithm>

extern "C" {
    struct Rect {
        int x, y, width, height;
    };

    int omni_sys_odinslides_pack(Rect* rects, int count, int max_width) {
        if (count <= 0 || max_width <= 0) return -1;
        
        int current_x = 0;
        int current_y = 0;
        int row_height = 0;
        int total_height = 0;

        for (int i = 0; i < count; ++i) {
            if (current_x + rects[i].width > max_width) {
                current_x = 0;
                current_y += row_height;
                row_height = 0;
            }
            rects[i].x = current_x;
            rects[i].y = current_y;
            current_x += rects[i].width;
            if (rects[i].height > row_height) {
                row_height = rects[i].height;
            }
        }
        total_height = current_y + row_height;
        return total_height;
    }
}
