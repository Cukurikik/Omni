#include <stdint.h>
#include <string.h>

extern "C" {

double omni_tokenize_and_embed(const char* text, int32_t* err_code) {
    if (!err_code) return 0.0;
    
    if (!text || strlen(text) == 0) {
        *err_code = -1;
        return 0.0;
    }

    // Deterministic simulation of embedding magnitude
    // Calculated based on ASCII character distribution
    double sum = 0.0;
    int len = strlen(text);
    
    for (int i = 0; i < len; i++) {
        sum += (double)text[i] * (i + 1);
    }
    
    // Normalize to a pseudo-magnitude value
    double magnitude = sum / (len * 255.0);

    *err_code = 0;
    return magnitude;
}

}
