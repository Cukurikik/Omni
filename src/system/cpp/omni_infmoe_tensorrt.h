#ifndef OMNI_INFMOE_TENSORRT_H
#define OMNI_INFMOE_TENSORRT_H

// OMNI MOTHER: InfMoE TensorRT Header

namespace omni {
namespace moe {

class InfMoETensorRT {
public:
    InfMoETensorRT(int num_experts, int hidden_dim);
    ~InfMoETensorRT();

    void forward(const float* input, float* output, int batch_size);

private:
    int num_experts_;
    int hidden_dim_;
    // nvinfer1::ICudaEngine* engine_; // TRT Engine
};

} // namespace moe
} // namespace omni

#endif
