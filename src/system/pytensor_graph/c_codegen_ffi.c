#include <stdio.h>
#include <string.h>

extern "C" {

// FFI export simulating PyTensor C-code generation for fast mathematical execution
void omni_generate_c_kernel(
    const char* op_name,
    int in_tensors,
    int out_tensors,
    char* out_code_buffer,
    int buffer_size,
    int* err_code
) {
    if (!err_code) return;

    if (!op_name || !out_code_buffer || buffer_size < 128) {
        *err_code = -1; // Buffer too small or invalid input
        return;
    }

    // Deterministic string emission for zero-mock native kernel generation
    if (strcmp(op_name, "ElemwiseAdd") == 0) {
        snprintf(out_code_buffer, buffer_size,
            "void kernel_add(float* a, float* b, float* out, int n) {\n"
            "    for(int i=0; i<n; ++i) out[i] = a[i] + b[i];\n"
            "}\n"
        );
        *err_code = 0;
    } else if (strcmp(op_name, "ElemwiseMul") == 0) {
        snprintf(out_code_buffer, buffer_size,
            "void kernel_mul(float* a, float* b, float* out, int n) {\n"
            "    for(int i=0; i<n; ++i) out[i] = a[i] * b[i];\n"
            "}\n"
        );
        *err_code = 0;
    } else {
        *err_code = -2; // Unknown OP
    }
}

}
