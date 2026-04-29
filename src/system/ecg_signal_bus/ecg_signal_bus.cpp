#include <iostream>
#include <vector>
#include <stdexcept>
#include <string>

class ECGBusError : public std::runtime_error {
public:
    explicit ECGBusError(const std::string& msg) : std::runtime_error(msg) {}
};

template <typename T>
class Result {
private:
    T value_;
    bool is_ok_;
    std::string error_msg_;

public:
    Result(T val) : value_(val), is_ok_(true) {}
    Result(const std::string& err) : is_ok_(false), error_msg_(err) {}

    bool is_ok() const { return is_ok_; }
    T unwrap() const {
        if (!is_ok_) throw ECGBusError(error_msg_);
        return value_;
    }
};

/**
 * OMNI Engine: ecg-bus
 * DMA level sensor reading logic extracting High Hz ECG geometries.
 */
class ECGSignalBusEngine {
private:
    double max_dma_latency_ms;

public:
    ECGSignalBusEngine(double latency_cap) : max_dma_latency_ms(latency_cap) {}

    Result<bool> extract_sensor_wave_frames(size_t sample_rate, double process_latency_ms) {
        if (sample_rate == 0) {
            return Result<bool>("Sample rate matrices impossible");
        }

        if (process_latency_ms > max_dma_latency_ms) {
            return Result<bool>("High-Hz ECG matrices delayed past latency failure point");
        }

        return Result<bool>(true);
    }
};
