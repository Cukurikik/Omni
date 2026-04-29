#include <vector>
#include <stdexcept>

namespace omni {
namespace caffe2 {

class Tensor {
private:
    std::vector<float> data;
    std::vector<int> shape;

public:
    Tensor(const std::vector<int>& dims) : shape(dims) {
        int size = 1;
        for (int d : dims) size *= d;
        data.resize(size, 0.0f);
    }

    float& at(int index) {
        if (index < 0 || index >= data.size()) {
            throw std::out_of_range("Tensor index out of bounds");
        }
        return data[index];
    }

    const std::vector<int>& get_shape() const { return shape; }
    
    // Matrix Multiplicaiton kernel O(N^3)
    static Tensor matmul(const Tensor& A, const Tensor& B) {
        if (A.shape.size() != 2 || B.shape.size() != 2 || A.shape[1] != B.shape[0]) {
            throw std::invalid_argument("Invalid shapes for matmul");
        }
        Tensor C({A.shape[0], B.shape[1]});
        for (int i = 0; i < A.shape[0]; ++i) {
            for (int j = 0; j < B.shape[1]; ++j) {
                float sum = 0;
                for (int k = 0; k < A.shape[1]; ++k) {
                    sum += A.data[i * A.shape[1] + k] * B.data[k * B.shape[1] + j];
                }
                C.data[i * B.shape[1] + j] = sum;
            }
        }
        return C;
    }
};

}
}
