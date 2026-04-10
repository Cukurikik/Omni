#include <vector>
#include <queue>
#include <mutex>
#include <string>
#include <memory>
#include <functional>

namespace omni_timescaledb {

struct Connection { int fd; bool alive; std::string endpoint; };

class ConnectionPool {
    std::vector<std::unique_ptr<Connection>> pool_;
    std::queue<Connection*> available_;
    std::mutex mtx_;
    size_t max_size_;
    std::string endpoint_;
public:
    ConnectionPool(const std::string& ep, size_t max_sz) : endpoint_(ep), max_size_(max_sz) {
        for (size_t i = 0; i < max_sz; i++) {
            auto c = std::make_unique<Connection>();
            c->fd = (int)i; c->alive = true; c->endpoint = ep;
            available_.push(c.get());
            pool_.push_back(std::move(c));
        }
    }
    Connection* acquire() {
        std::lock_guard<std::mutex> lock(mtx_);
        if (available_.empty()) return nullptr;
        auto* c = available_.front(); available_.pop(); return c;
    }
    void release(Connection* c) { std::lock_guard<std::mutex> lock(mtx_); if (c) available_.push(c); }
    size_t available_count() { std::lock_guard<std::mutex> lock(mtx_); return available_.size(); }
    size_t total_count() { return pool_.size(); }
    void drain() { std::lock_guard<std::mutex> lock(mtx_); while (!available_.empty()) available_.pop(); }
};

class RetryPolicy {
    int max_retries_; int backoff_ms_;
public:
    RetryPolicy(int max_r, int backoff) : max_retries_(max_r), backoff_ms_(backoff) {}
    bool should_retry(int attempt) { return attempt < max_retries_; }
    int get_delay(int attempt) { return backoff_ms_ * (1 << attempt); }
};

class CircuitBreaker {
    int failure_count_; int threshold_; bool open_;
public:
    CircuitBreaker(int thresh) : failure_count_(0), threshold_(thresh), open_(false) {}
    bool is_open() { return open_; }
    void record_failure() { if (++failure_count_ >= threshold_) open_ = true; }
    void record_success() { failure_count_ = 0; open_ = false; }
    void reset() { failure_count_ = 0; open_ = false; }
};

} // namespace