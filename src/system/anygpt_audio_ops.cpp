#include <vector>
#include <string>

struct AudioStreamResult {
    bool ok;
    std::string err;
};

AudioStreamResult process_audio_chunk(const std::vector<float>& pcm) {
    if (pcm.empty()) {
        return {false, "Empty PCM data"};
    }
    return {true, ""};
}
