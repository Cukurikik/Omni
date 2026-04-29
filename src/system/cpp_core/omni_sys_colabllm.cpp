#include <cstdint>

extern "C" {
    int omni_sys_colabllm_is_colab_env(const char* env_path) {
        if (!env_path) return 0;
        
        // Simple heuristic check for Colab directory structure
        const char* token = "/content";
        int len = 8;
        
        for (int i = 0; i < len; ++i) {
            if (env_path[i] != token[i]) return 0;
        }
        return 1;
    }
}
