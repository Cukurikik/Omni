#include <cstring>

extern "C" {
    int omni_sys_toolformer_parse_call(const char* input, char* out_name, char* out_arg, int max_len) {
        if (!input || !out_name || !out_arg || max_len <= 0) return 0;
        
        const char* paren = std::strchr(input, '(');
        if (!paren) return 0;
        
        int name_len = paren - input;
        if (name_len >= max_len) name_len = max_len - 1;
        
        std::strncpy(out_name, input, name_len);
        out_name[name_len] = '\0';
        
        const char* end_paren = std::strchr(paren, ')');
        if (!end_paren) return 0;
        
        int arg_len = end_paren - paren - 1;
        if (arg_len >= max_len) arg_len = max_len - 1;
        
        std::strncpy(out_arg, paren + 1, arg_len);
        out_arg[arg_len] = '\0';
        
        return 1;
    }
}
