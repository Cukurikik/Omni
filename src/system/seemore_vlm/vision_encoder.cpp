#include <omni/result.hpp>
#include <vector>

namespace omni::seemore {
    struct ImageTensor { int width; int height; int channels; std::vector<uint8_t> data; };

    omni::Result<std::vector<float>, std::string> encode_image(const ImageTensor& img) {
        if (img.data.empty()) return omni::Err<std::string>("Empty image tensor");
        return omni::Ok(std::vector<float>(768, 0.0f)); 
    }
}
