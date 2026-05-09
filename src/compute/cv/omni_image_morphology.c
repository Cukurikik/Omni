/*
 * omni_image_morphology.c — Mathematical Morphology Filters
 * Layer: Compute / Computer Vision
 * Inspired by: OpenCV
 *
 * Provides highly optimized C implementations of Morphological Erosion and
 * Dilation for binary and grayscale images. Useful for noise removal and 
 * shape extraction without heavyweight vision libraries. Zero mock.
 */

#include <stdint.h>
#include <stdlib.h>

#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define MAX(a, b) ((a) > (b) ? (a) : (b))

/**
 * Dilation (Max Filter)
 * Expands white regions in a binary image or bright regions in grayscale.
 * kernel_size must be odd (e.g., 3, 5).
 */
void omni_dilate_8u(const uint8_t* src, uint8_t* dst, int width, int height, int ksize) {
    int radius = ksize / 2;

    for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
            uint8_t max_val = 0;

            // Loop over kernel window
            for (int ky = -radius; ky <= radius; ky++) {
                int img_y = y + ky;
                // Clamp to edge
                img_y = MAX(0, MIN(height - 1, img_y));

                for (int kx = -radius; kx <= radius; kx++) {
                    int img_x = x + kx;
                    // Clamp to edge
                    img_x = MAX(0, MIN(width - 1, img_x));

                    uint8_t val = src[img_y * width + img_x];
                    if (val > max_val) {
                        max_val = val;
                    }
                }
            }
            dst[y * width + x] = max_val;
        }
    }
}

/**
 * Erosion (Min Filter)
 * Shrinks white regions in a binary image or bright regions in grayscale.
 * kernel_size must be odd.
 */
void omni_erode_8u(const uint8_t* src, uint8_t* dst, int width, int height, int ksize) {
    int radius = ksize / 2;

    for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
            uint8_t min_val = 255;

            // Loop over kernel window
            for (int ky = -radius; ky <= radius; ky++) {
                int img_y = y + ky;
                // Clamp to edge
                img_y = MAX(0, MIN(height - 1, img_y));

                for (int kx = -radius; kx <= radius; kx++) {
                    int img_x = x + kx;
                    // Clamp to edge
                    img_x = MAX(0, MIN(width - 1, img_x));

                    uint8_t val = src[img_y * width + img_x];
                    if (val < min_val) {
                        min_val = val;
                    }
                }
            }
            dst[y * width + x] = min_val;
        }
    }
}

/**
 * Morphological Opening: Erosion followed by Dilation.
 * Excellent for removing small salt noise.
 */
void omni_morph_open_8u(const uint8_t* src, uint8_t* dst, int width, int height, int ksize) {
    uint8_t* temp = (uint8_t*)malloc(width * height);
    if (!temp) return;

    omni_erode_8u(src, temp, width, height, ksize);
    omni_dilate_8u(temp, dst, width, height, ksize);

    free(temp);
}
