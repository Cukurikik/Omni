#include <omni/result.hpp>
#include <string>

namespace omni::envoy {

class ClusterManager {
public:
    omni::Result<bool, std::string> add_cluster(const std::string& name) {
        if (name.empty()) return omni::Err<std::string>("Name empty");
        return omni::Ok(true);
    }
};

}
