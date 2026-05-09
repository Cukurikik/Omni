# OMNI MOTHER Production Zero-Mock Thread Affinity
# C++ Linux utility to lock high-priority inference threads to specific CPU cores.
# This eliminates OS context switching latency for TensorRT-LLM and MLX threads.

#include <iostream>
#include <pthread.h>
#include <sched.h>
#include <stdexcept>
#include <vector>

namespace omni {
namespace system {
namespace thread {

class AffinityManager {
public:
    static bool pin_current_thread_to_core(int core_id) {
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(core_id, &cpuset);

        pthread_t current_thread = pthread_self();
        int result = pthread_setaffinity_np(current_thread, sizeof(cpu_set_t), &cpuset);

        if (result != 0) {
            std::cerr << "OMNI CRITICAL: pthread_setaffinity_np failed for core " 
                      << core_id << " with error code " << result << "\n";
            return false;
        }

        std::cout << "OMNI THREADING: Thread " << current_thread 
                  << " successfully pinned to CPU Core " << core_id << "\n";
        return true;
    }

    static bool pin_current_thread_to_cores(const std::vector<int>& core_ids) {
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        
        for (int core_id : core_ids) {
            CPU_SET(core_id, &cpuset);
        }

        pthread_t current_thread = pthread_self();
        int result = pthread_setaffinity_np(current_thread, sizeof(cpu_set_t), &cpuset);

        if (result != 0) {
            std::cerr << "OMNI CRITICAL: Failed to pin thread to multiple cores.\n";
            return false;
        }

        return true;
    }
};

} // namespace thread
} // namespace system
} // namespace omni
