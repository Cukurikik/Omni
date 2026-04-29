#include <string>

namespace omni {
namespace flame {

template<typename T>
struct OmniResult {
    T value;
    std::string error;
    bool is_ok;
};

class ThermalSensorFFI {
public:
    OmniResult<double> read_temperature() {
        // C++ low-level hardware interface for reading high-fidelity thermal sensors
        double temp_celsius = 450.5;
        
        return {temp_celsius, "", true};
    }
};

}
}
