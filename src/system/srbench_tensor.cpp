// OMNI System Layer - SRBench Tensor Ops
#include <vector>
#include <stdexcept>

namespace Omni {
namespace System {

template<typename T>
class Result {
public:
    T value;
    bool is_ok;
    const char* error_msg;

    static Result<T> Ok(T val) { return {val, true, nullptr}; }
    static Result<T> Err(const char* msg) { return {T(), false, msg}; }
};

class TensorOps {
public:
    static Result<double> ComputeVectorDot(const std::vector<double>& a, const std::vector<double>& b) {
        if (a.size() != b.size()) {
            return Result<double>::Err("Vector dimension mismatch");
        }
        
        double dot = 0.0;
        for (size_t i = 0; i < a.size(); ++i) {
            dot += a[i] * b[i];
        }
        return Result<double>::Ok(dot);
    }
};

}
}
