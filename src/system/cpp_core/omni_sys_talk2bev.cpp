#include <cstdint>

extern "C" {
    int omni_sys_talk2bev_check_collision(int x1, int y1, int r1, int x2, int y2, int r2) {
        // Circle collision mock for BEV objects
        int dx = x2 - x1;
        int dy = y2 - y1;
        int dist_sq = dx * dx + dy * dy;
        
        int r_sum = r1 + r2;
        int r_sum_sq = r_sum * r_sum;
        
        return (dist_sq <= r_sum_sq) ? 1 : 0;
    }
}
