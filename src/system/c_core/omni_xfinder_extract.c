/* Omni xFinder Answer Extractor (C) */
/* Ref: IAAR-Shanghai/xFinder — ICLR'25 */
#include <string.h>
#include <ctype.h>
char omni_extract_mc_answer(const char* response, int len) {
    for (int i = len - 1; i >= 0; --i) {
        char c = toupper(response[i]);
        if (c >= 'A' && c <= 'D') {
            if (i == 0 || !isalpha(response[i-1]))
                if (i == len-1 || !isalpha(response[i+1]))
                    return c;
        }
    }
    return '\0';
}
int omni_xfinder_evaluate(const char* pred, const char* gold) {
    if (!pred || !gold) return 0;
    return (toupper(pred[0]) == toupper(gold[0])) ? 1 : 0;
}
