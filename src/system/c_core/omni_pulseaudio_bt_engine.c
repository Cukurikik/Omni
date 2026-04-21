/*
 * omni_pulseaudio_bt_engine.c
 * Production-Grade PulseAudio Bluetooth Codec Engine
 * ==============================================================
 * Absorbed from: EHfive/pulseaudio-modules-bt
 *
 * Key patterns learned and implemented:
 * - Bluetooth A2DP codec capability negotiation
 * - LDAC/AAC/aptX/aptX-HD/SBC codec parameter computation
 * - Audio transport buffer sizing for BT streaming
 * - Codec priority ranking and selection algorithm
 * - Bitpool quality mapping for SBC encoder
 *
 * OMNI Layer: system/c_core
 * @since 2026.4.0
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define ENGINE_VERSION "1.0.0-omni"

/* ---------- Error Codes ---------- */
typedef enum {
    PA_BT_SUCCESS = 0,
    PA_BT_ERR_INVALID_CODEC,
    PA_BT_ERR_UNSUPPORTED_RATE,
    PA_BT_ERR_BUFFER_TOO_SMALL,
    PA_BT_ERR_NEGOTIATION_FAILED,
} pa_bt_error_t;

/* ---------- Codec Types ---------- */
typedef enum {
    CODEC_SBC = 0,
    CODEC_AAC,
    CODEC_APTX,
    CODEC_APTX_HD,
    CODEC_LDAC,
    CODEC_OPUS,
    CODEC_COUNT
} pa_bt_codec_t;

/* ---------- Codec Capabilities ---------- */
typedef struct {
    pa_bt_codec_t codec;
    const char*   name;
    int           max_bitrate_kbps;
    int           min_bitrate_kbps;
    int           latency_ms;
    int           priority;
    int           supports_44100;
    int           supports_48000;
    int           supports_96000;
    int           lossless_capable;
} pa_bt_codec_info_t;

static const pa_bt_codec_info_t CODEC_DB[CODEC_COUNT] = {
    { CODEC_SBC,     "SBC",      345,  128, 150, 1, 1, 1, 0, 0 },
    { CODEC_AAC,     "AAC",      320,   96, 100, 3, 1, 1, 0, 0 },
    { CODEC_APTX,    "aptX",     384,  384,  60, 4, 1, 1, 0, 0 },
    { CODEC_APTX_HD, "aptX HD",  576,  576,  80, 5, 1, 1, 0, 0 },
    { CODEC_LDAC,    "LDAC",     990,  330,  50, 6, 1, 1, 1, 1 },
    { CODEC_OPUS,    "Opus",     510,   64,  40, 2, 1, 1, 0, 0 },
};

/* ---------- A2DP Transport Config ---------- */
typedef struct {
    pa_bt_codec_t codec;
    int           sample_rate;
    int           channels;
    int           bit_depth;
    int           bitrate_kbps;
    int           mtu_bytes;
    int           buffer_frames;
    int           latency_ms;
} pa_bt_transport_config_t;

/* ---------- SBC Bitpool Config ---------- */
typedef struct {
    int min_bitpool;
    int max_bitpool;
    int optimal_bitpool;
    int quality_mode; /* 0=low, 1=medium, 2=high */
    int channel_mode; /* 0=mono, 1=dual, 2=stereo, 3=joint */
    int allocation;   /* 0=SNR, 1=loudness */
    int subbands;
    int block_length;
} pa_bt_sbc_config_t;

/**
 * Get codec information by type.
 *
 * @param codec  The codec type.
 * @param info   Output: codec capability structure.
 * @return PA_BT_SUCCESS or error code.
 */
pa_bt_error_t omni_pa_bt_get_codec_info(
    pa_bt_codec_t codec, pa_bt_codec_info_t* info)
{
    if (codec < 0 || codec >= CODEC_COUNT)
        return PA_BT_ERR_INVALID_CODEC;

    *info = CODEC_DB[codec];
    return PA_BT_SUCCESS;
}

/**
 * Negotiate the best codec from a list of supported codecs.
 *
 * @param supported   Array of supported codec types.
 * @param count       Number of supported codecs.
 * @param best_codec  Output: the selected codec.
 * @return PA_BT_SUCCESS or error code.
 */
pa_bt_error_t omni_pa_bt_negotiate_codec(
    const pa_bt_codec_t* supported, int count, pa_bt_codec_t* best_codec)
{
    if (count <= 0 || supported == NULL || best_codec == NULL)
        return PA_BT_ERR_NEGOTIATION_FAILED;

    int best_priority = -1;
    *best_codec = supported[0];

    for (int i = 0; i < count; i++) {
        if (supported[i] >= 0 && supported[i] < CODEC_COUNT) {
            int prio = CODEC_DB[supported[i]].priority;
            if (prio > best_priority) {
                best_priority = prio;
                *best_codec = supported[i];
            }
        }
    }

    return (best_priority >= 0) ? PA_BT_SUCCESS : PA_BT_ERR_NEGOTIATION_FAILED;
}

/**
 * Compute transport buffer configuration.
 *
 * @param codec       Selected codec.
 * @param sample_rate Audio sample rate.
 * @param channels    Number of channels.
 * @param config      Output: transport configuration.
 * @return PA_BT_SUCCESS or error code.
 */
pa_bt_error_t omni_pa_bt_compute_transport(
    pa_bt_codec_t codec, int sample_rate, int channels,
    pa_bt_transport_config_t* config)
{
    if (codec < 0 || codec >= CODEC_COUNT)
        return PA_BT_ERR_INVALID_CODEC;
    if (sample_rate != 44100 && sample_rate != 48000 && sample_rate != 96000)
        return PA_BT_ERR_UNSUPPORTED_RATE;

    const pa_bt_codec_info_t* ci = &CODEC_DB[codec];

    config->codec = codec;
    config->sample_rate = sample_rate;
    config->channels = channels;
    config->bit_depth = (codec == CODEC_APTX_HD || codec == CODEC_LDAC) ? 24 : 16;
    config->bitrate_kbps = ci->max_bitrate_kbps;
    config->latency_ms = ci->latency_ms;

    /* BT L2CAP MTU — typical for A2DP */
    config->mtu_bytes = 672;

    /* Buffer frames: enough to fill one MTU */
    int bytes_per_frame = channels * (config->bit_depth / 8);
    config->buffer_frames = (bytes_per_frame > 0)
        ? config->mtu_bytes / bytes_per_frame
        : 128;

    return PA_BT_SUCCESS;
}

/**
 * Compute SBC encoder configuration.
 *
 * @param quality  Quality level (0=low, 1=medium, 2=high).
 * @param channels Number of channels.
 * @param config   Output: SBC configuration.
 * @return PA_BT_SUCCESS.
 */
pa_bt_error_t omni_pa_bt_compute_sbc_config(
    int quality, int channels, pa_bt_sbc_config_t* config)
{
    config->subbands = 8;
    config->block_length = 16;
    config->allocation = 1; /* loudness */
    config->quality_mode = quality;

    if (channels == 1) {
        config->channel_mode = 0; /* mono */
        config->min_bitpool = 2;
        config->max_bitpool = (quality >= 2) ? 31 : (quality == 1) ? 19 : 12;
    } else {
        config->channel_mode = 3; /* joint stereo */
        config->min_bitpool = 2;
        config->max_bitpool = (quality >= 2) ? 53 : (quality == 1) ? 35 : 20;
    }

    config->optimal_bitpool = config->max_bitpool;
    return PA_BT_SUCCESS;
}

/**
 * Estimate audio latency for a given codec and buffer config.
 *
 * @param codec         Selected codec.
 * @param sample_rate   Sample rate.
 * @param buffer_frames Frames per buffer.
 * @return Estimated total latency in milliseconds.
 */
double omni_pa_bt_estimate_latency(
    pa_bt_codec_t codec, int sample_rate, int buffer_frames)
{
    if (codec < 0 || codec >= CODEC_COUNT || sample_rate <= 0)
        return -1.0;

    double codec_latency = (double)CODEC_DB[codec].latency_ms;
    double buffer_latency = (double)buffer_frames / (double)sample_rate * 1000.0;
    /* Add BT stack overhead (~20ms) and OS scheduling (~5ms) */
    double total = codec_latency + buffer_latency + 20.0 + 5.0;
    return total;
}
