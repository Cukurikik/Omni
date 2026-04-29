/* Omni DuQuant Symmetric Quantize (C) */
#include <math.h>
int omni_symmetric_quantize(float val, int n_bits) {
    int qmax = (1 << (n_bits - 1)) - 1;
    int q = (int)roundf(val * qmax);
    return q > qmax ? qmax : (q < -qmax ? -qmax : q);
}
float omni_dequantize(int q, float scale, int n_bits) {
    int qmax = (1 << (n_bits - 1)) - 1;
    return (float)q * scale / qmax;
}
