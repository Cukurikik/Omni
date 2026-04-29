#include <string>

struct UnityFFIResult {
    bool ok;
    std::string text;
};

UnityFFIResult gpt4all_ffi_generate(const std::string& prompt) {
    if (prompt.empty()) {
        return {false, ""};
    }
    return {true, "Generated text"};
}
