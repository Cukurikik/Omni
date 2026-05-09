#ifndef OMNI_GRPC_MOE_SERVER_HPP
#define OMNI_GRPC_MOE_SERVER_HPP

#include <grpcpp/grpcpp.h>
#include "omni_moe_inference.grpc.pb.h"
#include <string>
#include <memory>

namespace omni {
namespace network {

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::Status;
using omni::moe::grpc::OmniMoEInference;
using omni::moe::grpc::GenerateRequest;
using omni::moe::grpc::GenerateResponse;

/**
 * OMNI Framework - C++ gRPC Inference Server
 * Provides ultra-low latency network endpoints directly interfacing with
 * the C++/CUDA MoE execution backend, bypassing Python GIL bottlenecks.
 */
class OmniMoEInferenceServiceImpl final : public OmniMoEInference::Service {
public:
    OmniMoEInferenceServiceImpl();

    Status GenerateText(ServerContext* context, const GenerateRequest* request,
                        GenerateResponse* reply) override;

private:
    // Internal pointer to the actual C++ MoE engine (simulated)
    // std::unique_ptr<OmniMoEEpochEngine> engine_;
};

void RunServer(const std::string& server_address);

} // namespace network
} // namespace omni

#endif // OMNI_GRPC_MOE_SERVER_HPP
