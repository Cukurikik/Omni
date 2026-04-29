#include <stdint.h>
#include <stddef.h>

// Highly optimized alpha compositing for Background Matting
void omni_alpha_composite(
    const uint8_t* fg, const uint8_t* bg, const uint8_t* alpha, 
    uint8_t* out, size_t num_pixels) 
{
    for(size_t i = 0; i < num_pixels; i++) {
        uint32_t a = alpha[i];
        uint32_t inv_a = 255 - a;
        
        // RGB Channels
        for(int c=0; c<3; c++) {
            size_t idx = i*3 + c;
            uint32_t f = fg[idx];
            uint32_t b = bg[idx];
            out[idx] = (uint8_t)((f * a + b * inv_a) / 255);
        }
    }
}
