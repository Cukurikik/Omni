#ifndef OMNI_CUDNN_FRONTEND_WRAPPER_HPP
#define OMNI_CUDNN_FRONTEND_WRAPPER_HPP

#include <cudnn.h>
#include <cudnn_frontend.h>
#include <vector>
#include <memory>

namespace omni {
namespace system {
namespace cuda {

/**
 * OMNI Framework - cuDNN Frontend Wrapper (C++)
 * Utilizes the modern cuDNN Graph API (cudnn-frontend) to perform highly optimized 
 * Grouped GEMM operations required for MoE expert execution.
 */
class CudnnFrontendWrapper {
public:
    CudnnFrontendWrapper(int gpu_id);
    ~CudnnFrontendWrapper();

    void initialize();

    // Executes a Grouped GEMM for MoE: computes all expert FFNs simultaneously
    // A: [sum_tokens, d_model]
    // B: array of [num_experts] weights [d_model, d_ff]
    // C: [sum_tokens, d_ff]
    void execute_grouped_gemm(
        void* d_A,
        std::vector<void*> d_B_experts,
        void* d_C,
        const std::vector<int>& m_sizes, // tokens per expert
        int n_size,                      // d_ff
        int k_size                       // d_model
    );

private:
    int gpu_id_;
    cudnnHandle_t cudnn_handle_;
    bool initialized_;

    // Builds the operation graph for the backend
    cudnn_frontend::ExecutionPlan build_grouped_gemm_plan(int num_groups);
};

} // namespace cuda
} // namespace system
} // namespace omni

#endif // OMNI_CUDNN_FRONTEND_WRAPPER_HPP
