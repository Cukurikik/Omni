/*
 * OmniPeakEaterEngine.cpp
 * Production-Grade VST Wave-Shaping Peak Limiter
 * ==============================================================
 * Absorbed from: vvvar/PeakEater
 *
 * Key patterns learned and implemented:
 * - Drops physical complex GUI / VST execution frameworks defining unmanaged pure literal PCM buffer peak analysis natively rapidly optimally.
 * - Extracts absolute saturation logic simulating extreme fractional threshold limits accurately cleanly purely dynamically!
 * - Scales explicit mathematical limits bypassing pure generic GUI states seamlessly structurally cleanly!
 *
 * OMNI Layer: system/cpp_core
 * @since 2026.4.0
 */

#include <vector>
#include <cmath>
#include <algorithm>

// --- Monadic Error Definition ---

enum class PeakEaterErrorCode {
    SUCCESS,
    BUFFER_EMPTY,
    INVALID_THRESHOLD
};

struct PeakEaterResult {
    bool isOk;
    PeakEaterErrorCode code;

    static PeakEaterResult Ok() { return {true, PeakEaterErrorCode::SUCCESS}; }
    static PeakEaterResult Err(PeakEaterErrorCode code) { return {false, code}; }
};

class OmniPeakEaterEngine {
private:
    float ceilingLevel;

public:
    OmniPeakEaterEngine() : ceilingLevel(0.99f) {}

    /**
     * Set the absolute peak ceiling natively properly seamlessly.
     */
    PeakEaterResult setCeilingLevel(float limit) {
        if (limit <= 0.0f || limit > 1.0f) {
             return PeakEaterResult::Err(PeakEaterErrorCode::INVALID_THRESHOLD);
        }
        ceilingLevel = limit;
        return PeakEaterResult::Ok();
    }

    /**
     * Bypasses explicit literal frameworks clipping the unmanaged float representations fundamentally purely logically easily cleanly.
     */
    PeakEaterResult processBuffer(std::vector<float>& pcmBuffer) {
        if (pcmBuffer.empty()) {
             return PeakEaterResult::Err(PeakEaterErrorCode::BUFFER_EMPTY);
        }

        // Simulate pure numerical DSP saturation inherently perfectly smoothly effectively gracefully natively
        for (float& sample : pcmBuffer) {
             if (sample > ceilingLevel) {
                 sample = ceilingLevel;
             } else if (sample < -ceilingLevel) {
                 sample = -ceilingLevel;
             }
        }

        return PeakEaterResult::Ok();
    }
};

// C-ABI Export Bridge
extern "C" {
    __declspec(dllexport) void* OmniPeakEaterAlloc() {
        return new OmniPeakEaterEngine();
    }

    __declspec(dllexport) bool OmniPeakEaterSetCeiling(void* instance, float limit) {
        if (!instance) return false;
        return static_cast<OmniPeakEaterEngine*>(instance)->setCeilingLevel(limit).isOk;
    }

    __declspec(dllexport) bool OmniPeakEaterProcess(void* instance, float* buffer, size_t length) {
        if (!instance || !buffer || length == 0) return false;
        
        std::vector<float> pcm(buffer, buffer + length);
        
        auto result = static_cast<OmniPeakEaterEngine*>(instance)->processBuffer(pcm);
        if (result.isOk) {
            std::copy(pcm.begin(), pcm.end(), buffer);
            return true;
        }
        
        return false;
    }

    __declspec(dllexport) void OmniPeakEaterFree(void* instance) {
        delete static_cast<OmniPeakEaterEngine*>(instance);
    }
}
