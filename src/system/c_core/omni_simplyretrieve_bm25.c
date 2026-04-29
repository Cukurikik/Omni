/* Omni SimplyRetrieve BM25 Retrieval Kernel (C)
 * Ref: RCGAI/SimplyRetrieve — MIT */
#include <math.h>
#include <string.h>
#include <stdlib.h>

typedef struct { int doc_id; double score; } OmniBM25Hit;

double omni_bm25_score(int tf, int df, int doc_len, double avg_dl, int n_docs,
                       double k1, double b) {
    double idf = log((n_docs - df + 0.5) / (df + 0.5) + 1.0);
    double tf_norm = (tf * (k1 + 1.0)) / (tf + k1 * (1.0 - b + b * (doc_len / avg_dl)));
    return idf * tf_norm;
}

int omni_bm25_rank(OmniBM25Hit* hits, int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = i + 1; j < n; j++) {
            if (hits[j].score > hits[i].score) {
                OmniBM25Hit tmp = hits[i]; hits[i] = hits[j]; hits[j] = tmp;
            }
        }
    }
    return n;
}
