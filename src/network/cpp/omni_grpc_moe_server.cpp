#include "omni_grpc_moe_server.hpp"
#include <iostream>
#include <thread>
#include <chrono>

namespace omni {
namespace network {

OmniMoEInferenceServiceImpl::OmniMoEInferenceServiceImpl() {
    std::cout << "OMNI C++: Initializing native gRPC MoE Inference Service." << std::endl;
    // Here we would initialize the TensorRT-LLM or custom CUDA engine
}

Status OmniMoEInferenceServiceImpl::GenerateText(ServerContext* context, const GenerateRequest* request,
                                                 GenerateResponse* reply) {
    // Production validation
    if (request->prompt().empty()) {
        return Status(grpc::StatusCode::INVALID_ARGUMENT, "Prompt cannot be empty");
    }

    auto start = std::chrono::high_resolution_clock::now();

    // Simulated inference execution bridging to the C++/CUDA layers
    std::cout << "OMNI C++: Received request from tenant " << request->tenant_id() 
              << ". Forwarding to MoE CUDA Engine..." << std::endl;

    // Simulate compute time
    std::this_thread::sleep_for(std::chrono::milliseconds(150));

    std::string response_text = "OMNI Framework: Output generated via highly-optimized C++ native MoE engine.";
    
    auto end = std::chrono::high_resolution_clock::now();
    double elapsed = std::chrono::duration<double, std::milli>(end - start).count();

    reply->set_generated_text(response_text);
    reply->set_tokens_used(128); // Simulated token count
    reply->set_compute_time_ms(elapsed);

    return Status::OK;
}

void RunServer(const std::string& server_address) {
    OmniMoEInferenceServiceImpl service;
    ServerBuilder builder;
    
    // Listen on the given address without any authentication mechanism for this internal service.
    // Auth is handled by the API Gateway layer.
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    builder.RegisterService(&service);
    
    std::unique_ptr<Server> server(builder.BuildAndStart());
    std::cout << "OMNI C++: gRPC Server listening on " << server_address << std::endl;
    server->Wait();
}

} // namespace network
} // namespace omni

// Entry point
// int main(int argc, char** argv) {
//     omni::network::RunServer("0.0.0.0:50051");
//     return 0;
// }
