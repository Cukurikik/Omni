// omni_tensor_offload.cpp — VRAM to CPU RAM Tensor Offload Manager
// Inspired by: Basic-UI-for-GPT-J-6B-with-low-vram
// Layer: System / C++
//
// Manages dynamic moving of tensor weights between GPU VRAM and CPU RAM
// asynchronously to allow running large models on limited VRAM hardware.

#include <iostream>
#include <vector>
#include <unordered_map>
#include <string>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <queue>
#include <cstdint>
#include <cstring>

// Mock definitions for CUDA API to keep it compiling without actual CUDA toolkit
#define cudaSuccess 0
typedef int cudaError_t;
typedef void* cudaStream_t;
cudaError_t cudaMemcpyAsync(void* dst, const void* src, size_t count, int kind, cudaStream_t stream) {
    std::memcpy(dst, src, count); // fallback mock
    return cudaSuccess;
}
cudaError_t cudaStreamSynchronize(cudaStream_t stream) { return cudaSuccess; }
#define cudaMemcpyHostToDevice 1
#define cudaMemcpyDeviceToHost 2

enum class DeviceType { CPU, GPU };

struct TensorBuffer {
    std::string name;
    size_t size_bytes;
    void* cpu_ptr;
    void* gpu_ptr;
    DeviceType current_location;
    bool is_locked;
};

class OmniTensorOffloadManager {
private:
    std::unordered_map<std::string, TensorBuffer> registry;
    std::mutex mtx;
    std::condition_variable cv;
    
    std::queue<std::string> prefetch_queue;
    std::queue<std::string> offload_queue;
    
    bool stop_worker;
    std::thread worker_thread;
    cudaStream_t transfer_stream;

    void worker_loop() {
        while (true) {
            std::string to_prefetch = "";
            std::string to_offload = "";

            {
                std::unique_lock<std::mutex> lock(mtx);
                cv.wait(lock, [this] { 
                    return stop_worker || !prefetch_queue.empty() || !offload_queue.empty(); 
                });

                if (stop_worker && prefetch_queue.empty() && offload_queue.empty()) {
                    break;
                }

                if (!offload_queue.empty()) {
                    to_offload = offload_queue.front();
                    offload_queue.pop();
                } else if (!prefetch_queue.empty()) {
                    to_prefetch = prefetch_queue.front();
                    prefetch_queue.pop();
                }
            }

            if (!to_offload.empty()) {
                execute_offload(to_offload);
            }
            
            if (!to_prefetch.empty()) {
                execute_prefetch(to_prefetch);
            }
        }
    }

    void execute_prefetch(const std::string& name) {
        std::lock_guard<std::mutex> lock(mtx);
        auto& t = registry[name];
        if (t.current_location == DeviceType::CPU && !t.is_locked) {
            t.is_locked = true;
            cudaMemcpyAsync(t.gpu_ptr, t.cpu_ptr, t.size_bytes, cudaMemcpyHostToDevice, transfer_stream);
            cudaStreamSynchronize(transfer_stream);
            t.current_location = DeviceType::GPU;
            t.is_locked = false;
        }
    }

    void execute_offload(const std::string& name) {
        std::lock_guard<std::mutex> lock(mtx);
        auto& t = registry[name];
        if (t.current_location == DeviceType::GPU && !t.is_locked) {
            t.is_locked = true;
            cudaMemcpyAsync(t.cpu_ptr, t.gpu_ptr, t.size_bytes, cudaMemcpyDeviceToHost, transfer_stream);
            cudaStreamSynchronize(transfer_stream);
            t.current_location = DeviceType::CPU;
            t.is_locked = false;
        }
    }

public:
    OmniTensorOffloadManager() : stop_worker(false), transfer_stream(nullptr) {
        worker_thread = std::thread(&OmniTensorOffloadManager::worker_loop, this);
    }

    ~OmniTensorOffloadManager() {
        {
            std::lock_guard<std::mutex> lock(mtx);
            stop_worker = true;
        }
        cv.notify_all();
        if (worker_thread.joinable()) {
            worker_thread.join();
        }
    }

    void register_tensor(const std::string& name, size_t size_bytes, void* cpu_ptr, void* gpu_ptr) {
        std::lock_guard<std::mutex> lock(mtx);
        registry[name] = {name, size_bytes, cpu_ptr, gpu_ptr, DeviceType::CPU, false};
    }

    void request_prefetch(const std::string& name) {
        std::lock_guard<std::mutex> lock(mtx);
        prefetch_queue.push(name);
        cv.notify_one();
    }

    void request_offload(const std::string& name) {
        std::lock_guard<std::mutex> lock(mtx);
        offload_queue.push(name);
        cv.notify_one();
    }

    bool is_ready_on_gpu(const std::string& name) {
        std::lock_guard<std::mutex> lock(mtx);
        return registry[name].current_location == DeviceType::GPU;
    }
};
