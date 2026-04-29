/* Omni SuperKnowa BM25 Tokenizer (C) */
/* Ref: ibm-self-serve-assets/SuperKnowa */
#include <string.h>
#include <ctype.h>
int omni_bm25_tokenize(const char* text, char tokens[][64], int max_tokens) {
    int count = 0, ti = 0;
    for (int i = 0; text[i] && count < max_tokens; i++) {
        if (isalnum((unsigned char)text[i])) {
            if (ti < 63) tokens[count][ti++] = tolower((unsigned char)text[i]);
        } else {
            if (ti > 0) { tokens[count][ti] = '\0'; count++; ti = 0; }
        }
    }
    if (ti > 0 && count < max_tokens) { tokens[count][ti] = '\0'; count++; }
    return count;
}
