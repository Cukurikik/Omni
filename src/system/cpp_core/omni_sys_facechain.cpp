#include <cstdint>

extern "C" {
    void omni_sys_facechain_blend(uint8_t* base_img, const uint8_t* face_img, int size, float alpha) {
        if (!base_img || !face_img || size <= 0) return;
        
        for (int i = 0; i < size; ++i) {
            base_img[i] = (uint8_t)((1.0f - alpha) * base_img[i] + alpha * face_img[i]);
        }
    }
}
