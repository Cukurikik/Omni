#include <omni/result.hpp>
#include <cstdint>

namespace omni::faiss {

class VectorIndex {
public:
    virtual ~VectorIndex() = default;
    virtual omni::Result<void*, std::string> search(const float* query, int k) = 0;
};

}
