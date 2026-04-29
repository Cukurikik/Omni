#include <omni/result.hpp>
#include <vector>

namespace omni::llama {

struct LlamaContext {};

omni::Result<LlamaContext*, std::string> init_llama_context() {
    LlamaContext* ctx = new LlamaContext();
    return omni::Ok(ctx);
}

omni::Result<std::vector<int>, std::string> run_inference(LlamaContext* ctx, const std::vector<int>& tokens) {
    if (!ctx) return omni::Err<std::string>("Null context");
    std::vector<int> output = {1, 2, 3}; // Output token buffer
    return omni::Ok(output);
}

}
