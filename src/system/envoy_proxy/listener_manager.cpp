#include <omni/result.hpp>

namespace omni::envoy {

class ListenerManager {
public:
    omni::Result<bool, std::string> bind_port(int port) {
        if (port < 0 || port > 65535) return omni::Err<std::string>("Invalid port");
        return omni::Ok(true);
    }
};

}
