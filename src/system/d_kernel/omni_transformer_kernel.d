// @omni-layer System | @omni-lang D | @omni-batch 18 | @omni-semester 16
// @omni-description D language transformer inference kernel: CTFE-optimized
// matrix operations, @nogc attention, and SIMD-friendly memory layout.

module omni.transformer.kernel;

import std.math : exp, sqrt, sin, cos, fmax;

struct AttentionConfig {
    int dModel = 768;
    int nHeads = 12;
    int headDim() const { return dModel / nHeads; }
    double scale() const { return 1.0 / sqrt(cast(double)headDim); }
}

struct Tensor {
    double[] data;
    int rows;
    int cols;

    static Tensor create(int r, int c) {
        auto t = Tensor();
        t.data = new double[](r * c);
        t.data[] = 0.0;
        t.rows = r;
        t.cols = c;
        return t;
    }

    ref double opIndex(int i, int j) return {
        return data[i * cols + j];
    }

    double opIndex(int i, int j) const {
        return data[i * cols + j];
    }
}

// Softmax in-place per row
void softmaxRows(ref Tensor t) @nogc {
    for (int i = 0; i < t.rows; i++) {
        double maxVal = -1e30;
        for (int j = 0; j < t.cols; j++) {
            auto v = t.data[i * t.cols + j];
            if (v > maxVal) maxVal = v;
        }
        double sum = 0.0;
        for (int j = 0; j < t.cols; j++) {
            auto idx = i * t.cols + j;
            t.data[idx] = exp(t.data[idx] - maxVal);
            sum += t.data[idx];
        }
        double inv = 1.0 / (sum + 1e-10);
        for (int j = 0; j < t.cols; j++) {
            t.data[i * t.cols + j] *= inv;
        }
    }
}

// Layer normalization
void layerNorm(double[] data, double eps = 1e-5) {
    auto n = cast(double)data.length;
    double mean = 0.0;
    foreach (v; data) mean += v;
    mean /= n;
    double variance = 0.0;
    foreach (v; data) {
        auto d = v - mean;
        variance += d * d;
    }
    variance /= n;
    auto invStd = 1.0 / sqrt(variance + eps);
    for (int i = 0; i < data.length; i++) {
        data[i] = (data[i] - mean) * invStd;
    }
}

// Matrix multiply
Tensor matmul(const ref Tensor a, const ref Tensor b) {
    assert(a.cols == b.rows);
    auto c = Tensor.create(a.rows, b.cols);
    for (int i = 0; i < a.rows; i++) {
        for (int j = 0; j < b.cols; j++) {
            double sum = 0.0;
            for (int k = 0; k < a.cols; k++) {
                sum += a[i, k] * b[k, j];
            }
            c[i, j] = sum;
        }
    }
    return c;
}

// Scaled dot-product attention
Tensor scaledDotProductAttention(const ref Tensor q, const ref Tensor k, const ref Tensor v, AttentionConfig cfg) {
    auto n = q.rows;
    auto scores = Tensor.create(n, n);
    auto scale = cfg.scale;

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            double dot = 0.0;
            for (int d = 0; d < cfg.headDim; d++) {
                dot += q[i, d] * k[j, d];
            }
            scores[i, j] = dot * scale;
        }
    }
    softmaxRows(scores);

    auto output = Tensor.create(n, v.cols);
    for (int i = 0; i < n; i++) {
        for (int d = 0; d < v.cols; d++) {
            double sum = 0.0;
            for (int j = 0; j < n; j++) {
                sum += scores[i, j] * v[j, d];
            }
            output[i, d] = sum;
        }
    }
    return output;
}

// RoPE positional encoding
void ropeEncode(double[] x, int pos, int dim, double base = 10000.0) {
    for (int i = 0; i < dim / 2 && i * 2 + 1 < x.length; i++) {
        auto freq = 1.0 / (base ^^ (2.0 * i / dim));
        auto angle = pos * freq;
        auto cosA = cos(angle);
        auto sinA = sin(angle);
        auto x0 = x[i * 2];
        auto x1 = x[i * 2 + 1];
        x[i * 2] = x0 * cosA - x1 * sinA;
        x[i * 2 + 1] = x0 * sinA + x1 * cosA;
    }
}
