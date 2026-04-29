#include <vector>
#include <algorithm>
#include <limits>

namespace tiny_dnn {

class MaxPoolingLayer {
public:
    MaxPoolingLayer(int pool_size, int stride) 
        : pool_size_(pool_size), stride_(stride) {}

    std::vector<float> forward(const std::vector<float>& input, int in_channels, int width, int height) {
        int out_width = (width - pool_size_) / stride_ + 1;
        int out_height = (height - pool_size_) / stride_ + 1;
        std::vector<float> output(in_channels * out_width * out_height, 0.0f);

        for (int c = 0; c < in_channels; ++c) {
            for (int y = 0; y < out_height; ++y) {
                for (int x = 0; x < out_width; ++x) {
                    float max_val = std::numeric_limits<float>::lowest();
                    for (int py = 0; py < pool_size_; ++py) {
                        for (int px = 0; px < pool_size_; ++px) {
                            int in_y = y * stride_ + py;
                            int in_x = x * stride_ + px;
                            int in_idx = c * (width * height) + in_y * width + in_x;
                            if (input[in_idx] > max_val) {
                                max_val = input[in_idx];
                            }
                        }
                    }
                    output[c * (out_width * out_height) + y * out_width + x] = max_val;
                }
            }
        }
        return output;
    }

private:
    int pool_size_;
    int stride_;
};

} // namespace tiny_dnn
