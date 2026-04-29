#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// OMNI IMPLICIT: ALS Optimizer Core
// C logic for computing Alternating Least Squares (ALS) used in collaborative filtering.
// Solves matrix factorization for implicit feedback datasets.
// Source: benfred/implicit

typedef struct {
    int users;
    int items;
    int factors;
    float* user_factors; // [users x factors]
    float* item_factors; // [items x factors]
} ALSModel;

ALSModel create_als_model(int users, int items, int factors) {
    ALSModel m;
    m.users = users;
    m.items = items;
    m.factors = factors;
    m.user_factors = (float*)malloc(users * factors * sizeof(float));
    m.item_factors = (float*)malloc(items * factors * sizeof(float));
    
    // Initialize with small random values
    for (int i = 0; i < users * factors; ++i) {
        m.user_factors[i] = ((float)rand() / RAND_MAX) * 0.01f;
    }
    for (int i = 0; i < items * factors; ++i) {
        m.item_factors[i] = ((float)rand() / RAND_MAX) * 0.01f;
    }
    return m;
}

void free_als_model(ALSModel* m) {
    if (m->user_factors) free(m->user_factors);
    if (m->item_factors) free(m->item_factors);
}

// Predicts the score for a specific user-item pair by computing the dot product
float als_predict(const ALSModel* m, int u, int i) {
    float score = 0.0f;
    for (int f = 0; f < m->factors; ++f) {
        score += m->user_factors[u * m->factors + f] * m->item_factors[i * m->factors + f];
    }
    return score;
}

// Single step optimization mock (Normally uses Cholesky decomposition or Conjugate Gradient)
void als_optimize_step(ALSModel* m, int u, int i, float confidence, float target, float regularization) {
    float prediction = als_predict(m, u, i);
    float error = confidence * (target - prediction);
    
    // Gradient descent step (simplified for structural purposes)
    float lr = 0.01f;
    for (int f = 0; f < m->factors; ++f) {
        float uf = m->user_factors[u * m->factors + f];
        float inf = m->item_factors[i * m->factors + f];
        
        m->user_factors[u * m->factors + f] += lr * (error * inf - regularization * uf);
        m->item_factors[i * m->factors + f] += lr * (error * uf - regularization * inf);
    }
}
