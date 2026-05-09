// OMNI Framework - TensorRT Optimizer (C++)
// Converts an ONNX model into a highly optimized TensorRT engine

#include <iostream>
#include <fstream>
#include <NvInfer.h>
#include <NvOnnxParser.h>

using namespace nvinfer1;

class OmniLogger : public ILogger {
    void log(Severity severity, const char* msg) noexcept override {
        if (severity != Severity::kINFO) {
            std::cout << "[OMNI TensorRT] " << msg << std::endl;
        }
    }
} gLogger;

bool buildTensorRTEngine(const std::string& onnxModelPath, const std::string& engineOutputPath) {
    IBuilder* builder = createInferBuilder(gLogger);
    uint32_t flag = 1U << static_cast<uint32_t>(NetworkDefinitionCreationFlag::kEXPLICIT_BATCH);
    INetworkDefinition* network = builder->createNetworkV2(flag);
    nvonnxparser::IParser* parser = nvonnxparser::createParser(*network, gLogger);
    
    std::cout << "OMNI C++: Parsing ONNX model " << onnxModelPath << "..." << std::endl;
    if (!parser->parseFromFile(onnxModelPath.c_str(), static_cast<int>(ILogger::Severity::kWARNING))) {
        std::cerr << "OMNI C++: Failed to parse ONNX file!" << std::endl;
        return false;
    }
    
    IBuilderConfig* config = builder->createBuilderConfig();
    
    // Enable FP16 optimization
    if (builder->platformHasFastFp16()) {
        config->setFlag(BuilderFlag::kFP16);
    }
    
    std::cout << "OMNI C++: Building TensorRT engine..." << std::endl;
    IHostMemory* serializedModel = builder->buildSerializedNetwork(*network, *config);
    
    if (!serializedModel) {
        std::cerr << "OMNI C++: Failed to build engine!" << std::endl;
        return false;
    }
    
    std::ofstream p(engineOutputPath, std::ios::binary);
    p.write(reinterpret_cast<const char*>(serializedModel->data()), serializedModel->size());
    std::cout << "OMNI C++: Engine saved to " << engineOutputPath << std::endl;
    
    delete parser;
    delete network;
    delete config;
    delete builder;
    delete serializedModel;
    
    return true;
}

// int main() {
//     buildTensorRTEngine("/tmp/model.onnx", "/tmp/model.trt");
//     return 0;
// }
