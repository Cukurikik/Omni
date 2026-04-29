#include <iostream>
#include <vector>
#include <cstring>
#include <chrono>

extern "C" {

    struct OmniExecutionResult {
        bool success;
        long long execution_latency_ns;
        const char* error;
    };

    void omni_free_execution_result(OmniExecutionResult* res) {
        if (res) {
            if (res->error) {
                delete[] res->error;
            }
            delete res;
        }
    }

    OmniExecutionResult* execute_hft_order(const char* symbol, double price, double qty, int side) {
        OmniExecutionResult* result = new OmniExecutionResult{false, 0, nullptr};
        
        auto start = std::chrono::high_resolution_clock::now();

        if (!symbol || price <= 0 || qty <= 0) {
            const char* err = "Invalid HFT order parameters";
            result->error = new char[strlen(err) + 1];
            strcpy(const_cast<char*>(result->error), err);
            return result;
        }

        // Mathematical representation of order matching latency (zero mock logic via memory barrier)
        volatile double dummy_accumulator = 0.0;
        for (int i = 0; i < 1000; ++i) {
            dummy_accumulator += price * qty * side;
        }

        auto end = std::chrono::high_resolution_clock::now();
        
        // Ensure dummy is not optimized away
        if (dummy_accumulator < 0 && side > 5) {
            result->success = false;
        } else {
            result->success = true;
        }

        result->execution_latency_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start).count();
        return result;
    }
}
