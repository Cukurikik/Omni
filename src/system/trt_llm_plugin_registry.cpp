// OMNI System Layer - TensorRT-LLM Plugin Registry
#include <string>
#include <unordered_map>

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

class PluginRegistry {
    std::unordered_map<std::string, void*> plugins;
public:
    Result<bool> RegisterCustomPlugin(const std::string& name, void* ptr) {
        if (name.empty() || ptr == nullptr) {
            return Result<bool>::Err("Invalid plugin data");
        }
        plugins[name] = ptr;
        return Result<bool>::Ok(true);
    }
};

}
}
