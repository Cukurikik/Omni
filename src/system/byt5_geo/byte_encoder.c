/* @omni-layer System | @omni-source Yachay-AI/byt5-geotagging | @omni-lang C
 * @omni-description Byte encoder: UTF-8 byte-level tokenizer for ByT5 with
 * byte-to-embedding lookup and sequence padding/truncation.
 */
#include <stdint.h>
#include <string.h>

#define OMNI_MAX_BYTES 512
#define OMNI_BYTE_VOCAB 259  /* 256 byte values + PAD + EOS + UNK */
#define OMNI_PAD_ID 256
#define OMNI_EOS_ID 257
#define OMNI_UNK_ID 258

typedef struct {
    uint16_t token_ids[OMNI_MAX_BYTES];
    int length;
    int padded_length;
} OmniByteSequence;

typedef struct {
    int ok;
    OmniByteSequence seq;
    const char *error;
} OmniByteResult;

OmniByteResult omni_encode_bytes(const char *text, int max_len) {
    OmniByteResult result;
    result.ok = 1;
    result.error = NULL;
    if (!text) { result.ok = 0; result.error = "null input"; return result; }
    int text_len = (int)strlen(text);
    int actual_len = text_len < max_len ? text_len : max_len;
    actual_len = actual_len < OMNI_MAX_BYTES - 1 ? actual_len : OMNI_MAX_BYTES - 1;
    int i;
    for (i = 0; i < actual_len; i++) {
        result.seq.token_ids[i] = (uint16_t)((unsigned char)text[i]);
    }
    result.seq.token_ids[i++] = OMNI_EOS_ID;
    result.seq.length = i;
    /* Pad to max_len */
    int padded = max_len < OMNI_MAX_BYTES ? max_len : OMNI_MAX_BYTES;
    while (i < padded) {
        result.seq.token_ids[i++] = OMNI_PAD_ID;
    }
    result.seq.padded_length = padded;
    return result;
}

int omni_count_utf8_chars(const char *text, int n_bytes) {
    int count = 0;
    for (int i = 0; i < n_bytes && text[i]; ) {
        unsigned char c = (unsigned char)text[i];
        if (c < 0x80) i += 1;
        else if (c < 0xE0) i += 2;
        else if (c < 0xF0) i += 3;
        else i += 4;
        count++;
    }
    return count;
}

float omni_byte_entropy(const uint16_t *ids, int len) {
    int counts[OMNI_BYTE_VOCAB];
    memset(counts, 0, sizeof(counts));
    for (int i = 0; i < len; i++) {
        if (ids[i] < OMNI_BYTE_VOCAB) counts[ids[i]]++;
    }
    float entropy = 0.0f;
    for (int i = 0; i < OMNI_BYTE_VOCAB; i++) {
        if (counts[i] > 0) {
            float p = (float)counts[i] / len;
            entropy -= p * logf(p + 1e-8f);
        }
    }
    return entropy;
}
