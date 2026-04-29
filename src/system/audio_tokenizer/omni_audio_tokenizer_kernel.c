#include <stdint.h>
#include <string.h>
#include <math.h>

/* OMNI Audio Tokenizer Kernel — System Layer
 * Absorbing OpenMOSS/MOSS-TTS audio tokenization at the C FFI boundary.
 * Implements mu-law companding and frame segmentation for TTS pipelines.
 */

typedef enum { ATKERR_OK = 0, ATKERR_NULL = -1, ATKERR_OVERFLOW = -2 } AtkResult;

/* Mu-law companding: f(x) = sgn(x) * ln(1 + mu*|x|) / ln(1 + mu) */
static float mu_law_encode(float x, float mu) {
    float sign = x >= 0.0f ? 1.0f : -1.0f;
    float abs_x = x >= 0.0f ? x : -x;
    return sign * logf(1.0f + mu * abs_x) / logf(1.0f + mu);
}

static float mu_law_decode(float y, float mu) {
    float sign = y >= 0.0f ? 1.0f : -1.0f;
    float abs_y = y >= 0.0f ? y : -y;
    return sign * (powf(1.0f + mu, abs_y) - 1.0f) / mu;
}

AtkResult atk_encode_frames(const float* pcm, size_t pcm_len,
                            float* out, size_t out_capacity,
                            size_t frame_size, float mu) {
    if (!pcm || !out) return ATKERR_NULL;
    size_t num_frames = pcm_len / frame_size;
    if (num_frames * frame_size > out_capacity) return ATKERR_OVERFLOW;

    for (size_t i = 0; i < num_frames * frame_size; ++i) {
        out[i] = mu_law_encode(pcm[i], mu);
    }
    return ATKERR_OK;
}

AtkResult atk_decode_frames(const float* encoded, size_t enc_len,
                            float* out, size_t out_capacity, float mu) {
    if (!encoded || !out) return ATKERR_NULL;
    if (enc_len > out_capacity) return ATKERR_OVERFLOW;

    for (size_t i = 0; i < enc_len; ++i) {
        out[i] = mu_law_decode(encoded[i], mu);
    }
    return ATKERR_OK;
}

const char* atk_diagnostics(void) {
    return "{\"engine\":\"OmniAudioTokenizerKernel\",\"status\":\"Active\"}";
}
