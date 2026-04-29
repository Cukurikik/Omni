#include "audio_processor.cpp"
#include <cmath>
#include <algorithm>

namespace pedalboard {

class DistortionProcessor : public AudioProcessor {
public:
    explicit DistortionProcessor(float drive) : drive_(drive) {
        // drive maps to multiplier
        multiplier_ = std::pow(10.0f, drive_ / 20.0f);
    }

    void process(std::vector<float>& buffer, double sample_rate) override {
        // Soft clipping distortion
        for (auto& sample : buffer) {
            float x = sample * multiplier_;
            // Fast soft clip polynomial approximation
            if (x > 1.0f) {
                sample = 2.0f / 3.0f;
            } else if (x < -1.0f) {
                sample = -2.0f / 3.0f;
            } else {
                sample = x - (x * x * x) / 3.0f;
            }
        }
    }

private:
    float drive_;
    float multiplier_;
};

} // namespace pedalboard
