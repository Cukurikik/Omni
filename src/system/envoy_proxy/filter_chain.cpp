#include <omni/result.hpp>
#include <string>

namespace omni::envoy {

class FilterChain {
public:
    omni::Result<bool, std::string> apply_filters(const std::string& request) {
        if (request.empty()) return omni::Err<std::string>("Empty request");
        return omni::Ok(true);
    }
};

}
