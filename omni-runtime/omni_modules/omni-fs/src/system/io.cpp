// omni-fs/system/io.cpp
#include <fstream>
#include <string>
extern "C" {
    struct OmniError { uint32_t code; const char* msg; };
    struct FsResult { void* ptr; size_t len; OmniError err; uint8_t is_error; };
    
    FsResult omni_fs_read_all(const char* path) {
        std::ifstream file(path, std::ios::binary | std::ios::ate);
        if (!file.is_open()) return {nullptr, 0, {404, "File Not Found"}, 1};
        size_t size = file.tellg();
        file.seekg(0, std::ios::beg);
        char* buffer = (char*)malloc(size);
        file.read(buffer, size);
        return {buffer, size, {0, nullptr}, 0};
    }
}
