// @omni-layer System | @omni-source microsoft/GPTQ-for-LLaMa | @omni-lang C++
// @omni-description 4-bit dequantization kernel: unpacks INT4 weights to FP32
// with group-wise scale/zero-point recovery.
#include <vector>
#include <cstdint>
#include <cmath>

struct QuantizedWeight {
    std::vector<uint8_t> packed_data;
    std::vector<float> scales;
    std::vector<float> zeros;
    int n_rows, n_cols, group_size, bits;
};

class DequantKernel {
    int bits_;
    int group_size_;
public:
    DequantKernel(int bits = 4, int group_size = 128) : bits_(bits), group_size_(group_size) {}

    std::vector<float> dequantize_row(const uint8_t* packed, const float* scales,
                                       const float* zeros, int n_cols) const {
        std::vector<float> output(n_cols);
        int vals_per_byte = 8 / bits_;
        int mask = (1 << bits_) - 1;
        for (int j = 0; j < n_cols; ++j) {
            int byte_idx = j / vals_per_byte;
            int bit_offset = (j % vals_per_byte) * bits_;
            int q_val = (packed[byte_idx] >> bit_offset) & mask;
            int group = j / group_size_;
            output[j] = (static_cast<float>(q_val) - zeros[group]) * scales[group];
        }
        return output;
    }

    std::vector<std::vector<float>> dequantize_matrix(const QuantizedWeight& qw) const {
        std::vector<std::vector<float>> output(qw.n_rows);
        int n_groups = (qw.n_cols + qw.group_size - 1) / qw.group_size;
        int bytes_per_row = (qw.n_cols * qw.bits + 7) / 8;
        for (int i = 0; i < qw.n_rows; ++i) {
            output[i] = dequantize_row(
                qw.packed_data.data() + i * bytes_per_row,
                qw.scales.data() + i * n_groups,
                qw.zeros.data() + i * n_groups,
                qw.n_cols
            );
        }
        return output;
    }

    size_t compressed_size(int n_rows, int n_cols) const {
        int bytes_per_row = (n_cols * bits_ + 7) / 8;
        int n_groups = (n_cols + group_size_ - 1) / group_size_;
        return static_cast<size_t>(n_rows) * (bytes_per_row + n_groups * 8);
    }
};
