#include <stdint.h>
#include <stddef.h>

extern "C" {

// FFI export for deterministic scalar quantization of high-dimensional vectors
void omni_vector_quantize_int8(
    const double* input_vectors, 
    int32_t num_vectors, 
    int32_t dim, 
    int8_t* output_quantized, 
    double* out_scales, 
    int32_t* err_code
) {
    if (!err_code) return;
    
    if (!input_vectors || !output_quantized || !out_scales || num_vectors <= 0 || dim <= 0) {
        *err_code = -1;
        return;
    }

    // Deterministic mathematical implementation of Int8 absolute maximum symmetric quantization
    for (int32_t i = 0; i < num_vectors; ++i) {
        int32_t offset = i * dim;
        
        // 1. Find absolute maximum in the vector
        double abs_max = 0.0;
        for (int32_t j = 0; j < dim; ++j) {
            double val = input_vectors[offset + j];
            if (val < 0) val = -val;
            if (val > abs_max) abs_max = val;
        }

        // 2. Compute scaling factor
        // Prevent division by zero mathematically
        double scale = (abs_max > 0.0) ? (127.0 / abs_max) : 1.0;
        out_scales[i] = (abs_max > 0.0) ? (abs_max / 127.0) : 1.0; // inverse scale for dequantization

        // 3. Quantize to int8
        for (int32_t j = 0; j < dim; ++j) {
            double quantized_val = input_vectors[offset + j] * scale;
            
            // Deterministic rounding to nearest integer
            int32_t rounded = (int32_t)(quantized_val + (quantized_val >= 0 ? 0.5 : -0.5));
            
            // Clamp strictly
            if (rounded > 127) rounded = 127;
            if (rounded < -127) rounded = -127;
            
            output_quantized[offset + j] = (int8_t)rounded;
        }
    }

    *err_code = 0;
}

}
