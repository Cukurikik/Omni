#include <iostream>
#include <vector>
#include <stdexcept>
#include <string>
#include <cmath>

class LLMSysError : public std::runtime_error {
public:
    explicit LLMSysError(const std::string& msg) : std::runtime_error(msg) {}
};

template <typename T>
class Result {
private:
    T value_;
    bool is_ok_;
    std::string error_msg_;

public:
    Result(T val) : value_(val), is_ok_(true) {}
    Result(const std::string& err) : is_ok_(false), error_msg_(err) {}

    bool is_ok() const { return is_ok_; }
    T unwrap() const {
        if (!is_ok_) throw LLMSysError(error_msg_);
        return value_;
    }
};

/**
 * OMNI Engine: sys-llm
 * Low-level physical hardware boundary management for LLM execution contexts.
 */
class LLMSysManagerEngine {
private:
    size_t physical_memory_gb;
    size_t active_context_load;

public:
    LLMSysManagerEngine(size_t phys_mem_gb) : physical_memory_gb(phys_mem_gb), active_context_load(0) {}

    Result<bool> allocate_context_window(size_t request_gb) {
        if (request_gb == 0) {
            return Result<bool>("Context request volume geometrically null");
        }
        
        if (active_context_load + request_gb > physical_memory_gb) {
            return Result<bool>("Hardware memory constraint violated: Context OOM impending");
        }
        
        active_context_load += request_gb;
        return Result<bool>(true);
    }

    Result<double> compute_kv_cache_fractal_density(size_t cache_bytes, size_t total_tokens) {
        if (total_tokens == 0) {
            return Result<double>("Token divisor structural fault");
        }
        
        double density = static_cast<double>(cache_bytes) / static_cast<double>(total_tokens);
        if (density < 1.0) {
             return Result<double>("Information density mathematically eroded below bit limit");
        }
        
        return Result<double>(density);
    }
};
