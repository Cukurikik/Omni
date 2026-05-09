// @omni-layer System | @omni-source monologg/GoEmotions-pytorch
// @omni-description Emotion embedding lookup in C: cache-friendly 28-class emotion
// vector storage with SIMD-ready dot product scoring.
// @omni-lang C | @omni-batch 16 | @omni-semester 16

#include <stdlib.h>
#include <math.h>
#include <string.h>

#define N_EMOTIONS 28
#define MAX_DIM 768

typedef struct {
    float embeddings[N_EMOTIONS][MAX_DIM];
    float bias[N_EMOTIONS];
    int d_model;
} EmotionEmbeddingTable;

typedef struct {
    float scores[N_EMOTIONS];
    int top_emotion;
    float top_score;
    int status;
} EmotionScoreResult;

void emotion_table_init(EmotionEmbeddingTable *table, int d_model) {
    if (!table || d_model <= 0 || d_model > MAX_DIM) return;
    table->d_model = d_model;
    for (int i = 0; i < N_EMOTIONS; i++) {
        table->bias[i] = 0.0f;
        for (int j = 0; j < d_model; j++) {
            table->embeddings[i][j] = sinf((float)(i+1) * (float)(j+1) * 0.003f) * 0.02f;
        }
    }
}

EmotionScoreResult emotion_score(const EmotionEmbeddingTable *table, const float *input, int d) {
    EmotionScoreResult result;
    result.status = -1;
    if (!table || !input || d <= 0) return result;

    int dim = d < table->d_model ? d : table->d_model;
    float max_score = -1e30f;
    int max_idx = 0;

    for (int i = 0; i < N_EMOTIONS; i++) {
        float dot = table->bias[i];
        for (int j = 0; j < dim; j++) {
            dot += table->embeddings[i][j] * input[j];
        }
        result.scores[i] = 1.0f / (1.0f + expf(-dot));
        if (result.scores[i] > max_score) {
            max_score = result.scores[i];
            max_idx = i;
        }
    }
    result.top_emotion = max_idx;
    result.top_score = max_score;
    result.status = 0;
    return result;
}

float emotion_bce_loss(const float *logits, const int *targets, int n) {
    if (!logits || !targets || n <= 0) return -1.0f;
    float loss = 0.0f;
    for (int i = 0; i < n; i++) {
        float sig = 1.0f / (1.0f + expf(-logits[i]));
        sig = fmaxf(sig, 1e-7f);
        sig = fminf(sig, 1.0f - 1e-7f);
        loss -= targets[i] * logf(sig) + (1 - targets[i]) * logf(1.0f - sig);
    }
    return loss / n;
}
