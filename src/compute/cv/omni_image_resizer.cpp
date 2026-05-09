/*
 * omni_image_resizer.cpp — Bilinear Image Resizer
 * Layer: Compute / C++
 *
 * Implements a high-performance CPU-bound bilinear image resizing algorithm 
 * for vision preprocessing pipelines. Does not rely on external libraries 
 * like OpenCV. Zero mock.
 */

#include <vector>
#include <cstdint>
#include <cmath>
#include <stdexcept>

struct ImageBuffer {
    std::vector<uint8_t> data;
    int width;
    int height;
    int channels; // Usually 3 for RGB
};

class OmniBilinearResizer {
public:
    static ImageBuffer resize(const ImageBuffer& src, int target_w, int target_h) {
        if (src.data.empty() || src.width <= 0 || src.height <= 0 || src.channels <= 0) {
            throw std::invalid_argument("Invalid source image");
        }

        ImageBuffer dst;
        dst.width = target_w;
        dst.height = target_h;
        dst.channels = src.channels;
        dst.data.resize(target_w * target_h * src.channels);

        float x_ratio = static_cast<float>(src.width - 1) / target_w;
        float y_ratio = static_cast<float>(src.height - 1) / target_h;

        for (int i = 0; i < target_h; i++) {
            for (int j = 0; j < target_w; j++) {
                
                int x_l = static_cast<int>(std::floor(x_ratio * j));
                int y_l = static_cast<int>(std::floor(y_ratio * i));
                int x_h = static_cast<int>(std::ceil(x_ratio * j));
                int y_h = static_cast<int>(std::ceil(y_ratio * i));

                float x_weight = (x_ratio * j) - x_l;
                float y_weight = (y_ratio * i) - y_l;

                for (int c = 0; c < src.channels; c++) {
                    int a = src.data[(y_l * src.width + x_l) * src.channels + c];
                    int b = src.data[(y_l * src.width + x_h) * src.channels + c];
                    int c_val = src.data[(y_h * src.width + x_l) * src.channels + c];
                    int d = src.data[(y_h * src.width + x_h) * src.channels + c];

                    float pixel = a * (1 - x_weight) * (1 - y_weight) +
                                  b * x_weight * (1 - y_weight) +
                                  c_val * (y_weight) * (1 - x_weight) +
                                  d * x_weight * y_weight;

                    dst.data[(i * target_w + j) * src.channels + c] = static_cast<uint8_t>(pixel);
                }
            }
        }
        return dst;
    }
};
