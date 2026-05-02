/* @omni-domain System Layer (Watermark Detection)
   @omni-source various/markllm
   @omni-description MarkLLM Watermark mimicking steganographic token encoding in C.
   @omni-requirement zero-mock, monadic-error */
#include <stdlib.h>
#include <string.h>
typedef struct { void* data; char* error; int is_ok; } OmniResult;

typedef struct { int* green_list; int green_size; int vocab_size; float delta; } WatermarkConfig;

OmniResult watermark_init(WatermarkConfig* cfg, int vocab_size, float delta, float gamma) {
    OmniResult r;
    if (vocab_size <= 0) { r.data=NULL; r.error="Vocab must be > 0."; r.is_ok=0; return r; }
    cfg->vocab_size = vocab_size;
    cfg->delta = delta;
    cfg->green_size = (int)(vocab_size * gamma);
    cfg->green_list = (int*)malloc(cfg->green_size * sizeof(int));
    if (!cfg->green_list) { r.data=NULL; r.error="Alloc failed."; r.is_ok=0; return r; }
    for (int i = 0; i < cfg->green_size; i++) cfg->green_list[i] = i;
    r.data=cfg; r.error=NULL; r.is_ok=1; return r;
}

int is_green_token(WatermarkConfig* cfg, int token_id) {
    for (int i = 0; i < cfg->green_size; i++) {
        if (cfg->green_list[i] == token_id) return 1;
    }
    return 0;
}

OmniResult watermark_detect(WatermarkConfig* cfg, int* tokens, int len) {
    OmniResult r;
    if (!cfg || !tokens || len <= 0) { r.data=NULL; r.error="Invalid input."; r.is_ok=0; return r; }
    int green_count = 0;
    for (int i = 0; i < len; i++) {
        if (is_green_token(cfg, tokens[i])) green_count++;
    }
    double* score = (double*)malloc(sizeof(double));
    *score = (double)green_count / len;
    r.data=score; r.error=NULL; r.is_ok=1; return r;
}

void watermark_free(WatermarkConfig* cfg) {
    if (cfg && cfg->green_list) { free(cfg->green_list); cfg->green_list = NULL; }
}
