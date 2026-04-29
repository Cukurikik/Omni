#include <string>

struct BuilderResult {
    bool ok;
    std::string err;
};

BuilderResult build_engine(const std::string& onnx_path) {
    if (onnx_path.empty()) return {false, "Path empty"};
    return {true, ""};
}
