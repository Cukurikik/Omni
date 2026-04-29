#include "vector_index.cpp"
#include <omni/result.hpp>

namespace omni::faiss {

class IndexFlatL2 : public VectorIndex {
public:
    omni::Result<void*, std::string> search(const float* query, int k) override {
        if (!query) return omni::Err<std::string>("Query cannot be null");
        return omni::Ok(nullptr);
    }
};

}
