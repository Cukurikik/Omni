#include <vector>
#include <stdexcept>

namespace omni::flashlight {

class Tensor {
public:
    Tensor(std::vector<int> dims) : dims_(dims) {
        size_t size = 1;
        for (int d : dims) size *= d;
        data_.resize(size, 0.0f);
    }

    float* data() { return data_.data(); }
    const float* data() const { return data_.data(); }

    Tensor add(const Tensor& other) const {
        if (dims_ != other.dims_) throw std::runtime_error("Dim mismatch in Tensor Add");
        Tensor result(dims_);
        for (size_t i = 0; i < data_.size(); ++i) {
            result.data_[i] = data_[i] + other.data_[i];
        }
        return result;
    }

    Tensor relu() const {
        Tensor result(dims_);
        for (size_t i = 0; i < data_.size(); ++i) {
            result.data_[i] = data_[i] > 0.0f ? data_[i] : 0.0f;
        }
        return result;
    }

private:
    std::vector<int> dims_;
    std::vector<float> data_;
};

} // namespace omni::flashlight
