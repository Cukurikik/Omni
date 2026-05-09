// @omni-layer System | @omni-source huggingface/peft | @omni-lang C
// @omni-description LoRA GEMM kernel: fused low-rank matrix multiply A*B for
// efficient adapter inference without full weight materialization.
#include <stdlib.h>
#include <math.h>

typedef struct { float *data; int rows; int cols; } LoRAMatrix;

LoRAMatrix lora_alloc(int rows, int cols) {
    LoRAMatrix m; m.rows = rows; m.cols = cols;
    m.data = (float*)calloc(rows * cols, sizeof(float));
    return m;
}

void lora_free(LoRAMatrix *m) { if (m && m->data) { free(m->data); m->data = NULL; } }

int lora_fused_forward(const float *input, int n, int d_in,
                        const LoRAMatrix *A, const LoRAMatrix *B,
                        float scaling, float *output, int d_out) {
    if (!input || !A || !B || !output) return -1;
    int rank = A->cols;
    float *hidden = (float*)calloc(n * rank, sizeof(float));
    if (!hidden) return -1;
    for (int i = 0; i < n; i++) {
        for (int r = 0; r < rank; r++) {
            float sum = 0;
            int limit = d_in < A->rows ? d_in : A->rows;
            for (int j = 0; j < limit; j++) sum += input[i*d_in+j] * A->data[j*rank+r];
            hidden[i*rank+r] = sum;
        }
    }
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < d_out && j < B->cols; j++) {
            float sum = 0;
            for (int r = 0; r < rank; r++) sum += hidden[i*rank+r] * B->data[r*B->cols+j];
            output[i*d_out+j] += sum * scaling;
        }
    }
    free(hidden);
    return 0;
}

float lora_param_count(int d_in, int d_out, int rank) {
    return (float)(d_in * rank + rank * d_out);
}
