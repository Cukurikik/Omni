/* ===========================================================================
 * OMNI MIXER ENGINE (POLYLINGUAL REMEDIATION)
 * ===========================================================================
 * Absorbed From  : SoLoud + Python OmniAudioMixerEngine concepts
 * Logic Inherited: C / System Layer (Multi-Channel PCM Sample Mixer)
 * Domain Layer   : System (C Core)
 * ===========================================================================
 *
 * By studying SoLoud and the existing Python audio mixer, Mother learned
 * that real-time audio mixing is fundamentally pointer arithmetic:
 * summing N source buffers into one destination buffer, sample by sample,
 * with per-channel gain coefficients and hard clipping to prevent overflow.
 *
 * C is the only language where this can be expressed at bare-metal speed
 * with zero abstraction overhead—exactly as the OS audio callback expects.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define OMNI_MAX_CHANNELS 16
#define OMNI_MAX_BUFFER_SIZE 4096

/* A single audio channel in the mixer. */
typedef struct {
    float buffer[OMNI_MAX_BUFFER_SIZE];
    float gain;          /* Linear gain: 0.0 = silent, 1.0 = unity */
    float pan;           /* -1.0 = full left, 0.0 = center, 1.0 = full right */
    int   active;        /* 1 = contributing to mix, 0 = muted */
    int   sample_count;  /* Number of valid samples in buffer */
    char  label[32];
} OmniMixerChannel;

/* The master mixer state. */
typedef struct {
    OmniMixerChannel channels[OMNI_MAX_CHANNELS];
    float            master_out_L[OMNI_MAX_BUFFER_SIZE];
    float            master_out_R[OMNI_MAX_BUFFER_SIZE];
    float            master_gain;
    int              channel_count;
    int              output_length;
} OmniMixerEngine;

/* Initialize the mixer to a clean state. */
void omni_mixer_init(OmniMixerEngine *mixer) {
    memset(mixer, 0, sizeof(OmniMixerEngine));
    mixer->master_gain = 1.0f;
    mixer->channel_count = 0;
    mixer->output_length = 0;
}

/* Add a channel to the mixer. Returns channel index, or -1 on failure. */
int omni_mixer_add_channel(OmniMixerEngine *mixer, const char *label, float gain, float pan) {
    if (mixer->channel_count >= OMNI_MAX_CHANNELS) return -1;

    int idx = mixer->channel_count;
    OmniMixerChannel *ch = &mixer->channels[idx];
    memset(ch->buffer, 0, sizeof(ch->buffer));
    ch->gain = gain;
    ch->pan = pan;
    ch->active = 1;
    ch->sample_count = 0;
    strncpy(ch->label, label, sizeof(ch->label) - 1);

    mixer->channel_count++;
    return idx;
}

/* Write sample data into a channel's buffer (simulating audio source input). */
void omni_mixer_write_samples(OmniMixerEngine *mixer, int channel_idx,
                               const float *samples, int count) {
    if (channel_idx < 0 || channel_idx >= mixer->channel_count) return;
    if (count > OMNI_MAX_BUFFER_SIZE) count = OMNI_MAX_BUFFER_SIZE;

    OmniMixerChannel *ch = &mixer->channels[channel_idx];
    memcpy(ch->buffer, samples, count * sizeof(float));
    ch->sample_count = count;
}

/* Hard-clip a single sample to [-1.0, 1.0]. */
static inline float omni_hard_clip(float s) {
    if (s > 1.0f) return 1.0f;
    if (s < -1.0f) return -1.0f;
    return s;
}

/* Perform the mix-down: sum all active channels into master L/R output. */
void omni_mixer_process(OmniMixerEngine *mixer) {
    /* Determine output length = max of all channel sample counts */
    int max_len = 0;
    for (int c = 0; c < mixer->channel_count; c++) {
        if (mixer->channels[c].sample_count > max_len)
            max_len = mixer->channels[c].sample_count;
    }
    if (max_len > OMNI_MAX_BUFFER_SIZE) max_len = OMNI_MAX_BUFFER_SIZE;
    mixer->output_length = max_len;

    /* Clear master output */
    memset(mixer->master_out_L, 0, max_len * sizeof(float));
    memset(mixer->master_out_R, 0, max_len * sizeof(float));

    /* Sum each active channel into the master bus with panning */
    for (int c = 0; c < mixer->channel_count; c++) {
        OmniMixerChannel *ch = &mixer->channels[c];
        if (!ch->active) continue;

        /* Constant-power pan law: L = cos(angle), R = sin(angle) */
        float angle = (ch->pan + 1.0f) * 0.25f * 3.14159265f; /* 0..PI/2 */
        float pan_l = cosf(angle);
        float pan_r = sinf(angle);

        for (int i = 0; i < ch->sample_count && i < max_len; i++) {
            float s = ch->buffer[i] * ch->gain;
            mixer->master_out_L[i] += s * pan_l;
            mixer->master_out_R[i] += s * pan_r;
        }
    }

    /* Apply master gain and hard-clip */
    for (int i = 0; i < max_len; i++) {
        mixer->master_out_L[i] = omni_hard_clip(mixer->master_out_L[i] * mixer->master_gain);
        mixer->master_out_R[i] = omni_hard_clip(mixer->master_out_R[i] * mixer->master_gain);
    }
}

void omni_mixer_diagnostics(const OmniMixerEngine *mixer) {
    printf("{\"engine\": \"OmniMixerEngine\", \"layer\": \"C System\", "
           "\"channels\": %d, \"output_samples\": %d, \"master_gain\": %.2f, "
           "\"learned_logic\": [\"pointer-arithmetic-summing\", "
           "\"constant-power-pan-law\", \"hard-clip-saturation\", "
           "\"zero-copy-memcpy-input\"]}\n",
           mixer->channel_count, mixer->output_length, mixer->master_gain);
}

int main(void) {
    OmniMixerEngine mixer;
    omni_mixer_init(&mixer);

    /* Create 3 channels: kick, snare, hihat */
    int kick  = omni_mixer_add_channel(&mixer, "Kick",  0.9f, -0.2f);
    int snare = omni_mixer_add_channel(&mixer, "Snare", 0.7f,  0.1f);
    int hihat = omni_mixer_add_channel(&mixer, "HiHat", 0.5f,  0.6f);

    /* Write synthetic sample data */
    float kick_data[]  = {0.8f, 0.6f, 0.3f, 0.1f};
    float snare_data[] = {0.0f, 0.0f, 0.9f, 0.7f};
    float hihat_data[] = {0.2f, 0.4f, 0.2f, 0.4f};

    omni_mixer_write_samples(&mixer, kick,  kick_data,  4);
    omni_mixer_write_samples(&mixer, snare, snare_data, 4);
    omni_mixer_write_samples(&mixer, hihat, hihat_data, 4);

    /* Process the mix */
    omni_mixer_process(&mixer);

    /* Output result */
    printf("Master L: [%.3f, %.3f, %.3f, %.3f]\n",
           mixer.master_out_L[0], mixer.master_out_L[1],
           mixer.master_out_L[2], mixer.master_out_L[3]);
    printf("Master R: [%.3f, %.3f, %.3f, %.3f]\n",
           mixer.master_out_R[0], mixer.master_out_R[1],
           mixer.master_out_R[2], mixer.master_out_R[3]);

    omni_mixer_diagnostics(&mixer);
    return 0;
}
