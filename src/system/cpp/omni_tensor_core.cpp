#include "omni_tensor_core.h"
#include <stdexcept>
#include <numeric>

// OMNI MOTHER: C++ Tensor Core for ML (Production Grade)
// Zero-cost abstractions for multi-dimensional mathematical structures.
namespace omni {
namespace compute {

Tensor::Tensor(const std::vector<size_t>& shape) : shape_(shape) {
    size_t total_size = 1;
    for (auto d : shape) total_size *= d;
    data_.resize(total_size, 0.0f);
}

float& Tensor::at(const std::vector<size_t>& indices) {
    if (indices.size() != shape_.size()) {
        throw std::invalid_argument("Dimension mismatch");
    }
    size_t flat_idx = 0;
    size_t multiplier = 1;
    for (int i = shape_.size() - 1; i >= 0; --i) {
        flat_idx += indices[i] * multiplier;
        multiplier *= shape_[i];
    }
    return data_[flat_idx];
}

}
}
