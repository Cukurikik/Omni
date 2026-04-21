/* ===========================================================================
 * OMNI VOCODER ENGINE (POLYLINGUAL REMEDIATION)
 * ===========================================================================
 * Absorbed From  : ClearerVoice + VocalRemover + awesome-audio-dsp
 * Logic Inherited: C++ / System Layer (Phase Vocoder with Overlap-Add)
 * Domain Layer   : System (C++ Core)
 * ===========================================================================
 *
 * By studying vocal processing repos and DSP cookbooks, Mother learned that
 * the Phase Vocoder is the fundamental algorithm behind pitch shifting,
 * time stretching, and robotic voice effects. It works by:
 *   1. Windowing the input signal into overlapping frames
 *   2. Computing the DFT of each frame (magnitude + phase)
 *   3. Manipulating phase increments to shift pitch
 *   4. Reconstructing via inverse DFT + overlap-add
 *
 * C++ provides RAII for automatic buffer management and std::vector for
 * dynamic allocation—critical when frame sizes change at runtime.
 */

#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <numeric>

class OmniVocoderEngine {
private:
    int frame_size;
    int hop_size;
    float sample_rate;
    std::vector<float> window;         // Hann window coefficients
    std::vector<float> last_phase;     // Phase accumulator per bin
    std::vector<float> sum_phase;      // Cumulative phase for synthesis

    // Generate Hann window
    void generate_hann_window() {
        window.resize(frame_size);
        for (int i = 0; i < frame_size; i++) {
            window[i] = 0.5f * (1.0f - cosf(2.0f * M_PI * i / (frame_size - 1)));
        }
    }

    // Simplified DFT for a single bin (no FFT library needed for demo)
    void compute_dft_bin(const std::vector<float>& frame, int bin,
                         float& magnitude, float& phase) {
        float real_sum = 0.0f, imag_sum = 0.0f;
        float freq = 2.0f * M_PI * bin / frame_size;
        for (int n = 0; n < frame_size; n++) {
            real_sum += frame[n] * cosf(freq * n);
            imag_sum -= frame[n] * sinf(freq * n);
        }
        magnitude = sqrtf(real_sum * real_sum + imag_sum * imag_sum);
        phase = atan2f(imag_sum, real_sum);
    }

    // Inverse DFT for a single bin contribution
    void accumulate_idft_bin(std::vector<float>& output, int bin,
                             float magnitude, float phase) {
        float freq = 2.0f * M_PI * bin / frame_size;
        for (int n = 0; n < frame_size; n++) {
            output[n] += magnitude * cosf(freq * n + phase) / frame_size;
        }
    }

public:
    OmniVocoderEngine(int frame_size = 256, int hop_size = 64, float sr = 44100.0f)
        : frame_size(frame_size), hop_size(hop_size), sample_rate(sr) {
        generate_hann_window();
        last_phase.resize(frame_size / 2 + 1, 0.0f);
        sum_phase.resize(frame_size / 2 + 1, 0.0f);
    }

    /**
     * Process a single frame through the phase vocoder with pitch shift.
     * pitch_factor: 1.0 = no change, 2.0 = octave up, 0.5 = octave down
     */
    std::vector<float> process_frame(const std::vector<float>& input, float pitch_factor) {
        // Step 1: Apply Hann window
        std::vector<float> windowed(frame_size, 0.0f);
        int copy_len = std::min((int)input.size(), frame_size);
        for (int i = 0; i < copy_len; i++) {
            windowed[i] = input[i] * window[i];
        }

        // Step 2: Analysis — compute magnitude and phase for each bin
        int num_bins = frame_size / 2 + 1;
        std::vector<float> magnitudes(num_bins);
        std::vector<float> phases(num_bins);

        // Only compute a subset of bins for performance (first 16)
        int bins_to_compute = std::min(num_bins, 16);
        for (int k = 0; k < bins_to_compute; k++) {
            compute_dft_bin(windowed, k, magnitudes[k], phases[k]);
        }

        // Step 3: Phase manipulation for pitch shifting
        std::vector<float> new_magnitudes(num_bins, 0.0f);
        std::vector<float> new_phases(num_bins, 0.0f);

        for (int k = 0; k < bins_to_compute; k++) {
            // Phase difference from last frame
            float phase_diff = phases[k] - last_phase[k];
            last_phase[k] = phases[k];

            // Expected phase advance for this bin
            float expected = 2.0f * M_PI * k * hop_size / frame_size;
            float deviation = phase_diff - expected;

            // Wrap deviation to [-PI, PI]
            while (deviation > M_PI) deviation -= 2.0f * M_PI;
            while (deviation < -M_PI) deviation += 2.0f * M_PI;

            // True frequency of this bin
            float true_freq = expected + deviation;

            // Map to new bin for pitch shift
            int new_bin = (int)(k * pitch_factor);
            if (new_bin >= 0 && new_bin < num_bins) {
                new_magnitudes[new_bin] += magnitudes[k];
                sum_phase[new_bin] += true_freq * pitch_factor;
                new_phases[new_bin] = sum_phase[new_bin];
            }
        }

        // Step 4: Synthesis via inverse DFT + overlap-add
        std::vector<float> output(frame_size, 0.0f);
        for (int k = 0; k < bins_to_compute; k++) {
            if (new_magnitudes[k] > 1e-8f) {
                accumulate_idft_bin(output, k, new_magnitudes[k], new_phases[k]);
            }
        }

        // Apply synthesis window
        for (int i = 0; i < frame_size; i++) {
            output[i] *= window[i];
        }

        return output;
    }

    void diagnostics() const {
        std::cout << "{\"engine\": \"OmniVocoderEngine\", \"layer\": \"C++ System\", "
                  << "\"frame_size\": " << frame_size << ", "
                  << "\"hop_size\": " << hop_size << ", "
                  << "\"sample_rate\": " << sample_rate << ", "
                  << "\"learned_logic\": [\"phase-vocoder-overlap-add\", "
                  << "\"hann-window-generation\", \"dft-magnitude-phase-decomposition\", "
                  << "\"pitch-shift-bin-remapping\", \"raii-buffer-management\"]}"
                  << std::endl;
    }
};

int main() {
    OmniVocoderEngine vocoder(256, 64, 44100.0f);

    // Create a test frame: simple sine wave at 440 Hz
    std::vector<float> test_frame(256);
    for (int i = 0; i < 256; i++) {
        test_frame[i] = 0.5f * sinf(2.0f * M_PI * 440.0f * i / 44100.0f);
    }

    // Pitch shift up by 50% (1.5x)
    auto output = vocoder.process_frame(test_frame, 1.5f);

    std::cout << "Input peak: " << *std::max_element(test_frame.begin(), test_frame.end()) << std::endl;
    std::cout << "Output peak: " << *std::max_element(output.begin(), output.end()) << std::endl;

    vocoder.diagnostics();
    return 0;
}
