#include <vector>
#include <string>

struct AllocResult {
    bool ok;
    int block_id;
    std::string error;
};

AllocResult allocate_block() {
    return {true, 42, ""};
}
