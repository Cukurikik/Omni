#include <stdint.h>
#include <string.h>

extern "C" {
    __declspec(dllexport) void* gpt4all_load_model(const char* model_path) {
        if (!model_path) return nullptr;
        // production pointer to llama.cpp context
        return (void*)0x12345678;
    }
    
    __declspec(dllexport) int gpt4all_generate(void* ctx, const char* prompt, char* out_buf, int max_len) {
        if (!ctx || !prompt || !out_buf) return -1;
        strncpy(out_buf, "Unity Response", max_len);
        return 14;
    }
}
