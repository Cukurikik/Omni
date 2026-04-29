#include <stdlib.h>

// Core SVM logic for EasyPR character recognition
double svm_predict(const double* features, const double* weights, double bias, int feature_len) {
    double sum = 0.0;
    for (int i = 0; i < feature_len; i++) {
        sum += features[i] * weights[i];
    }
    return sum + bias;
}

int classify_character(const double* features, const double* weights, double bias, int feature_len) {
    double val = svm_predict(features, weights, bias, feature_len);
    return (val > 0) ? 1 : 0;
}
