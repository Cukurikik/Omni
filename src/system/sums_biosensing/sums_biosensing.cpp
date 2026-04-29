#include <iostream>
#include <vector>
#include <stdexcept>
#include <string>

class SUMSError : public std::runtime_error {
public:
    explicit SUMSError(const std::string& msg) : std::runtime_error(msg) {}
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
        if (!is_ok_) throw SUMSError(error_msg_);
        return value_;
    }
};

/**
 * OMNI Engine: sums
 * Low level multi-camera buffer sync for high altitude biosensing signals (rPPG).
 */
class SUMSBiosensingEngine {
private:
    double max_jitter_tolerance_ms;

public:
    SUMSBiosensingEngine(double jitter) : max_jitter_tolerance_ms(jitter) {}

    Result<bool> synchronize_camera_buffers(std::vector<double> camera_timestamps) {
        if (camera_timestamps.empty()) {
            return Result<bool>("Camera array topology physically zero");
        }

        double max_time = camera_timestamps[0];
        double min_time = camera_timestamps[0];

        for (double t : camera_timestamps) {
            if (t > max_time) max_time = t;
            if (t < min_time) min_time = t;
        }

        double jitter = max_time - min_time;

        if (jitter > max_jitter_tolerance_ms) {
            return Result<bool>("Hardware synchronization jitter destroyed biosignal integrity");
        }

        return Result<bool>(true);
    }
};
