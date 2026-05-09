#ifndef OMNI_TENSOR_CORE_H
#define OMNI_TENSOR_CORE_H

#include <vector>

namespace omni {
namespace compute {

class Tensor {
public:
    Tensor(const std::vector<size_t>& shape);
    float& at(const std::vector<size_t>& indices);
    const std::vector<float>& data() const { return data_; }
    const std::vector<size_t>& shape() const { return shape_; }

private:
    std::vector<size_t> shape_;
    std::vector<float> data_;
};

}
}
#endif
