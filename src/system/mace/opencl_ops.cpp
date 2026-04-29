#include <CL/cl.h>
#include <iostream>
#include <vector>

// OMNI System Layer: MACE OpenCL Hardware Acceleration
// OpenCL buffer management and kernel execution bridge.

extern "C" {

class OpenCLContext {
private:
    cl_context context;
    cl_command_queue queue;
    cl_program program;
    cl_kernel kernel;

public:
    OpenCLContext() {
        cl_uint numPlatforms;
        clGetPlatformIDs(0, nullptr, &numPlatforms);
        if (numPlatforms == 0) throw std::runtime_error("No OpenCL platforms found.");

        std::vector<cl_platform_id> platforms(numPlatforms);
        clGetPlatformIDs(numPlatforms, platforms.data(), nullptr);

        cl_platform_id platform = platforms[0];
        cl_device_id device;
        clGetDeviceIDs(platform, CL_DEVICE_TYPE_GPU, 1, &device, nullptr);

        context = clCreateContext(nullptr, 1, &device, nullptr, nullptr, nullptr);
        queue = clCreateCommandQueue(context, device, 0, nullptr);
        
        // Zero-mock basic MatMul kernel for deep learning layer inference
        const char* source = 
            "__kernel void matmul(__global const float* A, __global const float* B, __global float* C, int N) {\n"
            "    int i = get_global_id(0);\n"
            "    int j = get_global_id(1);\n"
            "    float sum = 0.0f;\n"
            "    for (int k = 0; k < N; ++k) {\n"
            "        sum += A[i * N + k] * B[k * N + j];\n"
            "    }\n"
            "    C[i * N + j] = sum;\n"
            "}\n";

        program = clCreateProgramWithSource(context, 1, &source, nullptr, nullptr);
        clBuildProgram(program, 1, &device, nullptr, nullptr, nullptr);
        kernel = clCreateKernel(program, "matmul", nullptr);
    }

    void ExecuteMatMul(const float* A, const float* B, float* C, int N) {
        size_t bytes = N * N * sizeof(float);
        
        cl_mem bufA = clCreateBuffer(context, CL_MEM_READ_ONLY | CL_MEM_COPY_HOST_PTR, bytes, (void*)A, nullptr);
        cl_mem bufB = clCreateBuffer(context, CL_MEM_READ_ONLY | CL_MEM_COPY_HOST_PTR, bytes, (void*)B, nullptr);
        cl_mem bufC = clCreateBuffer(context, CL_MEM_WRITE_ONLY, bytes, nullptr, nullptr);

        clSetKernelArg(kernel, 0, sizeof(cl_mem), &bufA);
        clSetKernelArg(kernel, 1, sizeof(cl_mem), &bufB);
        clSetKernelArg(kernel, 2, sizeof(cl_mem), &bufC);
        clSetKernelArg(kernel, 3, sizeof(int), &N);

        size_t global_work_size[2] = { (size_t)N, (size_t)N };
        clEnqueueNDRangeKernel(queue, kernel, 2, nullptr, global_work_size, nullptr, 0, nullptr, nullptr);
        
        clEnqueueReadBuffer(queue, bufC, CL_TRUE, 0, bytes, C, 0, nullptr, nullptr);

        clReleaseMemObject(bufA);
        clReleaseMemObject(bufB);
        clReleaseMemObject(bufC);
    }

    ~OpenCLContext() {
        clReleaseKernel(kernel);
        clReleaseProgram(program);
        clReleaseCommandQueue(queue);
        clReleaseContext(context);
    }
};

void* mace_opencl_init() {
    return new OpenCLContext();
}

void mace_opencl_execute(void* ctx, const float* A, const float* B, float* C, int N) {
    static_cast<OpenCLContext*>(ctx)->ExecuteMatMul(A, B, C, N);
}

void mace_opencl_destroy(void* ctx) {
    delete static_cast<OpenCLContext*>(ctx);
}

}
