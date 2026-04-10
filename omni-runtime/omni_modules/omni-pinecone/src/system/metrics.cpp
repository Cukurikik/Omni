#include <atomic>
#include <string>
#include <unordered_map>
#include <chrono>
#include <mutex>
#include <vector>

namespace omni_pinecone {

class MetricsCollector {
    std::unordered_map<std::string, std::atomic<uint64_t>> counters_;
    std::unordered_map<std::string, std::atomic<int64_t>> gauges_;
    std::mutex mtx_;
public:
    void inc_counter(const std::string& name, uint64_t val = 1) { counters_[name].fetch_add(val); }
    uint64_t get_counter(const std::string& name) { return counters_[name].load(); }
    void set_gauge(const std::string& name, int64_t val) { gauges_[name].store(val); }
    int64_t get_gauge(const std::string& name) { return gauges_[name].load(); }
    void reset() {
        for (auto& [k, v] : counters_) v.store(0);
        for (auto& [k, v] : gauges_) v.store(0);
    }
};

class LatencyTracker {
    std::vector<double> samples_; std::mutex mtx_; double total_ = 0;
public:
    void record(double ms) { std::lock_guard<std::mutex> l(mtx_); samples_.push_back(ms); total_ += ms; }
    double avg() { std::lock_guard<std::mutex> l(mtx_); return samples_.empty() ? 0 : total_ / samples_.size(); }
    double p99() {
        std::lock_guard<std::mutex> l(mtx_);
        if (samples_.empty()) return 0;
        auto sorted = samples_; std::sort(sorted.begin(), sorted.end());
        return sorted[(size_t)(sorted.size() * 0.99)];
    }
    size_t count() { std::lock_guard<std::mutex> l(mtx_); return samples_.size(); }
};

} // namespace