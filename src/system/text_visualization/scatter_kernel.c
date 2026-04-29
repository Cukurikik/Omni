#include <stdint.h>

extern "C" {

double omni_calculate_scatter_coordinate(double tf1, double tf2, int32_t* err_code) {
    if (!err_code) return 0.0;
    
    if (tf1 < 0.0 || tf2 < 0.0) {
        *err_code = -1;
        return 0.0;
    }

    // Deterministic algorithm for mapping two corpus frequencies to a 1D scatter rank score
    // using purely mathematical log-odds ratio
    double odds1 = tf1 / (1.0 - tf1 + 1e-9);
    double odds2 = tf2 / (1.0 - tf2 + 1e-9);
    
    double score = odds1 - odds2; // Simplified Log-Odds

    *err_code = 0;
    return score;
}

}
