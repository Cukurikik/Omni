// ===========================================================================
// OMNI SYSTEM LAYER — LOSSLESSSWITCHER AUDIO STREAM INTERCEPTOR
// ===========================================================================
// Source Paradigm : vincentneo/LosslessSwitcher
// Domain Layer   : System (RAII pattern, OS audio subsystem)
// Language        : C++
// Function        : Monitors audio playback logs, detects sample rate and
//                   bit depth changes, and automatically reconfigures the
//                   system audio output device to match the source format —
//                   preventing unwanted OS-level resampling
// ===========================================================================

#include <string>
#include <vector>
#include <cstdint>
#include <cstdio>
#include <cstring>

namespace omni::audio {

// ---- Audio Format Descriptor ----------------------------------------------

struct AudioFormat {
    uint32_t sample_rate;     // Hz (e.g. 44100, 48000, 96000, 192000)
    uint16_t bit_depth;       // bits (e.g. 16, 24, 32)
    uint16_t channels;        // 1 = mono, 2 = stereo, etc.
    bool     is_lossless;
    char     codec[32];       // "ALAC", "FLAC", "AAC", "MP3", etc.
};

struct AudioDevice {
    char     name[256];
    char     uid[128];
    uint32_t current_sample_rate;
    uint16_t current_bit_depth;
    bool     supports_exclusive_mode;
    uint32_t supported_rates[16];
    int      supported_rate_count;
};

// ---- Log Parser (mirrors LosslessSwitcher's Apple Music log reader) -------

class MusicLogParser {
public:
    MusicLogParser() {
        printf("[LOSSLESS-OMNI-CPP] Log parser initialized.\n");
    }

    /// Parse a log line for sample rate information.
    /// Example log: "now playing: codec=ALAC, sampleRate=96000, bitDepth=24"
    bool parse_log_line(const char* line, AudioFormat& out_format) {
        // Search for "sampleRate=" pattern
        const char* sr_pos = strstr(line, "sampleRate=");
        if (!sr_pos) return false;

        out_format.sample_rate = 0;
        out_format.bit_depth = 16;
        out_format.channels = 2;
        out_format.is_lossless = false;
        strncpy(out_format.codec, "UNKNOWN", sizeof(out_format.codec) - 1);

        // Extract sample rate
        sscanf(sr_pos, "sampleRate=%u", &out_format.sample_rate);
        if (out_format.sample_rate == 0) return false;

        // Extract bit depth
        const char* bd_pos = strstr(line, "bitDepth=");
        if (bd_pos) {
            sscanf(bd_pos, "bitDepth=%hu", &out_format.bit_depth);
        }

        // Extract codec
        const char* codec_pos = strstr(line, "codec=");
        if (codec_pos) {
            sscanf(codec_pos, "codec=%31[^,\n ]", out_format.codec);
        }

        // Determine if lossless
        out_format.is_lossless = (strcmp(out_format.codec, "ALAC") == 0 ||
                                   strcmp(out_format.codec, "FLAC") == 0 ||
                                   out_format.bit_depth >= 24);

        printf("[LOSSLESS-OMNI-CPP] Detected: %s %uHz/%ubit (lossless=%s)\n",
               out_format.codec, out_format.sample_rate, out_format.bit_depth,
               out_format.is_lossless ? "yes" : "no");

        return true;
    }
};

// ---- Sample Rate Switcher -------------------------------------------------

class SampleRateSwitcher {
public:
    explicit SampleRateSwitcher(AudioDevice device)
        : device_(device), switch_count_(0) {
        printf("[LOSSLESS-OMNI-CPP] Switcher bound to device: %s (current: %uHz)\n",
               device_.name, device_.current_sample_rate);
    }

    /// Check if the device supports the target sample rate.
    bool supports_rate(uint32_t rate) const {
        for (int i = 0; i < device_.supported_rate_count; ++i) {
            if (device_.supported_rates[i] == rate) return true;
        }
        return false;
    }

    /// Find the best matching sample rate (exact match or nearest multiple).
    uint32_t best_match(uint32_t target) const {
        if (supports_rate(target)) return target;

        // Try integer multiples/divisors
        uint32_t candidates[] = { target * 2, target / 2, 44100, 48000, 96000, 192000 };
        for (auto c : candidates) {
            if (supports_rate(c)) return c;
        }

        // Fallback to highest supported
        uint32_t best = device_.supported_rates[0];
        for (int i = 1; i < device_.supported_rate_count; ++i) {
            if (device_.supported_rates[i] > best) best = device_.supported_rates[i];
        }
        return best;
    }

    /// Apply the new sample rate to the audio device.
    /// Production: calls AudioObjectSetPropertyData via Core Audio.
    bool apply_rate(uint32_t new_rate) {
        if (device_.current_sample_rate == new_rate) {
            printf("[LOSSLESS-OMNI-CPP] Already at %uHz — no switch needed.\n", new_rate);
            return true;
        }

        uint32_t actual = best_match(new_rate);
        printf("[LOSSLESS-OMNI-CPP] Switching: %uHz → %uHz%s\n",
               device_.current_sample_rate, actual,
               actual != new_rate ? " (nearest match)" : "");

        // Production: AudioObjectSetPropertyData(deviceID, &addr, ...)
        device_.current_sample_rate = actual;
        switch_count_++;
        return true;
    }

    /// Process a detected audio format and auto-switch if needed.
    bool process_format(const AudioFormat& format) {
        printf("[LOSSLESS-OMNI-CPP] Processing format: %s %uHz/%ubit\n",
               format.codec, format.sample_rate, format.bit_depth);

        if (!format.is_lossless) {
            printf("[LOSSLESS-OMNI-CPP] Lossy format — skipping switch.\n");
            return false;
        }

        return apply_rate(format.sample_rate);
    }

    uint32_t get_switch_count() const { return switch_count_; }
    uint32_t get_current_rate() const { return device_.current_sample_rate; }

private:
    AudioDevice device_;
    uint32_t    switch_count_;
};

} // namespace omni::audio

// int main() {
//     using namespace omni::audio;
//     AudioDevice dev = {};
//     strncpy(dev.name, "DAC Pro", 255);
//     dev.current_sample_rate = 44100;
//     dev.supported_rates[0] = 44100; dev.supported_rates[1] = 48000;
//     dev.supported_rates[2] = 96000; dev.supported_rates[3] = 192000;
//     dev.supported_rate_count = 4;
//
//     MusicLogParser parser;
//     SampleRateSwitcher switcher(dev);
//
//     const char* log = "now playing: codec=ALAC, sampleRate=96000, bitDepth=24";
//     AudioFormat fmt;
//     if (parser.parse_log_line(log, fmt)) { switcher.process_format(fmt); }
//     return 0;
// }
