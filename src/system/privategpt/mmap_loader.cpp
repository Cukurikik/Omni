#include <iostream>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string>
#include <stdexcept>

// OMNI PRIVATEGPT: Local Weight Loader via Memory Mapping
// Loads multi-gigabyte LLM model weights instantly via mmap, bypassing RAM limits on local machines.
// Source: imartinez/privateGPT (Underlying GGML integration mechanics)

namespace omni::privategpt {

enum class LoaderError {
    SUCCESS,
    FILE_NOT_FOUND,
    FSTAT_FAILED,
    MMAP_FAILED
};

template<typename T>
struct Result {
    T value;
    LoaderError error;
    bool is_ok() const { return error == LoaderError::SUCCESS; }
};

class MMapModel {
private:
    int fd;
    size_t size;
    void* addr;

public:
    MMapModel() : fd(-1), size(0), addr(MAP_FAILED) {}

    Result<bool> load(const std::string& filepath) {
        fd = open(filepath.c_str(), O_RDONLY);
        if (fd < 0) {
            return {false, LoaderError::FILE_NOT_FOUND};
        }

        struct stat st;
        if (fstat(fd, &st) < 0) {
            close(fd);
            fd = -1;
            return {false, LoaderError::FSTAT_FAILED};
        }
        size = st.st_size;

        // MAP_SHARED allows OS to page memory in and out transparently
        addr = mmap(nullptr, size, PROT_READ, MAP_SHARED, fd, 0);
        if (addr == MAP_FAILED) {
            close(fd);
            fd = -1;
            return {false, LoaderError::MMAP_FAILED};
        }

        // Hint to OS that we will read sequentially initially (useful for model validation)
        madvise(addr, size, MADV_SEQUENTIAL);

        return {true, LoaderError::SUCCESS};
    }

    void* get_data() const { return addr; }
    size_t get_size() const { return size; }

    ~MMapModel() {
        if (addr != MAP_FAILED) {
            munmap(addr, size);
        }
        if (fd >= 0) {
            close(fd);
        }
    }
};

} // namespace omni::privategpt
