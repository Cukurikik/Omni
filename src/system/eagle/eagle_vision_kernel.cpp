#include <vector>
#include <cmath>
#include <variant>
#include <string>
// @omni-domain System Layer (Vision Kernel)
// @omni-source NVlabs/EAGLE
// @omni-description Eagle Vision Kernel mimicking GPU convolution in C++.
// @omni-requirement zero-mock, monadic-error
struct KernelError { std::string message; };
template <typename T> using OmniResult = std::variant<T, KernelError>;

class EagleVisionKernel {
public:
    OmniResult<std::vector<float>> depthwise_conv2d(const std::vector<float>& input, int h, int w, const std::vector<float>& kernel, int ksize) {
        if (input.empty() || kernel.empty()) return KernelError{"Empty input or kernel."};
        if ((int)kernel.size() != ksize * ksize) return KernelError{"Kernel size mismatch."};
        int pad = ksize / 2;
        std::vector<float> output(h * w, 0.0f);
        for (int i = 0; i < h; i++) {
            for (int j = 0; j < w; j++) {
                float sum = 0;
                for (int ki = 0; ki < ksize; ki++) {
                    for (int kj = 0; kj < ksize; kj++) {
                        int ni = i + ki - pad, nj = j + kj - pad;
                        if (ni >= 0 && ni < h && nj >= 0 && nj < w)
                            sum += input[ni * w + nj] * kernel[ki * ksize + kj];
                    }
                }
                output[i * w + j] = sum;
            }
        }
        return output;
    }
    OmniResult<std::vector<float>> relu(const std::vector<float>& input) {
        if (input.empty()) return KernelError{"Empty input."};
        std::vector<float> out(input.size());
        for (size_t i = 0; i < input.size(); i++) out[i] = std::max(0.0f, input[i]);
        return out;
    }
};
