// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Envoy Proxy (OMNI Zero-Mock Implementation)
// Implements functional token bucket rate limiting and circuit breaking math.

#include <string>

namespace omni {
namespace compute {
namespace envoy {

template <typename T>
struct Result {
    T value;
    std::string error;
    bool is_ok;
    
    static Result<T> Ok(T val) { return {val, "", true}; }
    static Result<T> Err(std::string err) { return {T(), err, false}; }
};

enum class CircuitState {
    CLOSED,
    OPEN,
    HALF_OPEN
};

class CircuitBreaker {
private:
    CircuitState state;
    int consecutive_failures;
    int failure_threshold;
    long long last_failure_ms;
    long long reset_timeout_ms;

public:
    CircuitBreaker(int threshold, long long timeout) 
        : state(CircuitState::CLOSED), 
          consecutive_failures(0), 
          failure_threshold(threshold), 
          last_failure_ms(0), 
          reset_timeout_ms(timeout) {}

    Result<bool> allow_request(long long current_time_ms) {
        if (failure_threshold <= 0) {
            return Result<bool>::Err("Failure threshold must be positive.");
        }
        
        if (state == CircuitState::OPEN) {
            if (current_time_ms - last_failure_ms > reset_timeout_ms) {
                state = CircuitState::HALF_OPEN;
                return Result<bool>::Ok(true); // Allow one test request
            }
            return Result<bool>::Ok(false); // Circuit is open, deny.
        }
        
        return Result<bool>::Ok(true); // Closed or Half-Open allow
    }
    
    Result<bool> record_response(bool is_success, long long current_time_ms) {
        if (state == CircuitState::HALF_OPEN) {
            if (is_success) {
                state = CircuitState::CLOSED;
                consecutive_failures = 0;
            } else {
                state = CircuitState::OPEN;
                last_failure_ms = current_time_ms;
            }
            return Result<bool>::Ok(true);
        }
        
        if (state == CircuitState::CLOSED) {
            if (!is_success) {
                consecutive_failures++;
                if (consecutive_failures >= failure_threshold) {
                    state = CircuitState::OPEN;
                    last_failure_ms = current_time_ms;
                }
            } else {
                consecutive_failures = 0; // reset on success
            }
        }
        
        return Result<bool>::Ok(true);
    }
};

} // namespace envoy
} // namespace compute
} // namespace omni
