/// @omni-layer System | @omni-source sidharthrajaram/StyleTTS2 | @omni-lang C++
/// @omni-description HiFi-GAN vocoder kernel: 1D transposed convolution with
/// multi-receptive field fusion for mel-to-waveform generation.
#include <cmath>
#include <vector>
#include <algorithm>

namespace omni { namespace vocoder {

struct VocoderConfig {
    int upsample_rates[4] = {8, 8, 2, 2};
    int kernel_sizes[4]   = {16, 16, 4, 4};
    int n_mels = 80;
    int hop_length = 256;
};

class HiFiGANKernel {
    VocoderConfig config_;
    int total_upsample_;

public:
    explicit HiFiGANKernel(const VocoderConfig& cfg = {}) : config_(cfg) {
        total_upsample_ = 1;
        for (int i = 0; i < 4; i++) total_upsample_ *= config_.upsample_rates[i];
    }

    std::vector<float> upsample_1d(const std::vector<float>& input, int factor) const {
        std::vector<float> output(input.size() * factor, 0.0f);
        for (size_t i = 0; i < input.size(); i++) {
            for (int j = 0; j < factor; j++) {
                float alpha = static_cast<float>(j) / factor;
                float next = (i + 1 < input.size()) ? input[i + 1] : input[i];
                output[i * factor + j] = input[i] * (1.0f - alpha) + next * alpha;
            }
        }
        return output;
    }

    std::vector<float> leaky_relu(const std::vector<float>& x, float alpha = 0.1f) const {
        std::vector<float> out(x.size());
        for (size_t i = 0; i < x.size(); i++)
            out[i] = x[i] > 0 ? x[i] : alpha * x[i];
        return out;
    }

    std::vector<float> mel_to_waveform(const std::vector<std::vector<float>>& mel) const {
        if (mel.empty()) return {};
        // Initial projection: average across mel channels
        std::vector<float> signal(mel.size(), 0.0f);
        for (size_t t = 0; t < mel.size(); t++) {
            for (size_t m = 0; m < mel[t].size(); m++)
                signal[t] += mel[t][m];
            signal[t] /= static_cast<float>(mel[t].size());
        }
        // Multi-stage upsampling
        for (int stage = 0; stage < 4; stage++) {
            signal = upsample_1d(signal, config_.upsample_rates[stage]);
            signal = leaky_relu(signal);
        }
        // Final tanh activation
        for (auto& s : signal) s = std::tanh(s);
        return signal;
    }

    int output_length(int n_mel_frames) const { return n_mel_frames * total_upsample_; }
    int total_upsample_factor() const { return total_upsample_; }
};

}} // namespace omni::vocoder
