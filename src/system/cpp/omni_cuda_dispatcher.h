#ifndef OMNI_CUDA_DISPATCHER_H
#define OMNI_CUDA_DISPATCHER_H

#define private public
#include "omni_tensor_core.h"
#undef private

namespace omni {
namespace compute {

class CudaDispatcher {
public:
    void dispatch_matmul(Tensor& a, Tensor& b, Tensor& c);
};

}
}
#endif
