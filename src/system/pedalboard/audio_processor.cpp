#include <vector>
#include <cmath>

namespace pedalboard {

class AudioProcessor {
public:
    virtual ~AudioProcessor() = default;
    
    // Process a block of audio (in-place)
    virtual void process(std::vector<float>& buffer, double sample_rate) = 0;
};

// Hardcore implementation of a basic Gain processor
class GainProcessor : public AudioProcessor {
public:
    explicit GainProcessor(float gain_db) {
        set_gain_db(gain_db);
    }

    void set_gain_db(float gain_db) {
        gain_linear_ = std::pow(10.0f, gain_db / 20.0f);
    }

    void process(std::vector<float>& buffer, double sample_rate) override {
        for (auto& sample : buffer) {
            sample *= gain_linear_;
        }
    }

private:
    float gain_linear_;
};

} // namespace pedalboard
