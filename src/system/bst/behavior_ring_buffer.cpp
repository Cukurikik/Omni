// @omni-layer System | @omni-source jiwidi/Behavior-Sequence-Transformer-Pytorch
// @omni-description Behavior sequence ring buffer in C++: fixed-size circular buffer
// for user interaction history with O(1) append and retrieval.
// @omni-lang C++ | @omni-batch 16 | @omni-semester 16
#include <vector>
#include <cstdint>
#include <algorithm>
#include <variant>
#include <string>

struct BSTError { std::string msg; };
template<typename T> using OmniResult = std::variant<T, BSTError>;

struct InteractionEvent {
    int64_t item_id;
    int64_t timestamp;
    float rating;
    uint8_t event_type; // 0=view, 1=click, 2=purchase
};

class BehaviorRingBuffer {
    std::vector<InteractionEvent> buffer_;
    size_t capacity_;
    size_t head_ = 0;
    size_t count_ = 0;
public:
    explicit BehaviorRingBuffer(size_t capacity) : capacity_(capacity), buffer_(capacity) {}

    void push(InteractionEvent event) {
        buffer_[head_] = event;
        head_ = (head_ + 1) % capacity_;
        if (count_ < capacity_) ++count_;
    }

    OmniResult<std::vector<InteractionEvent>> get_recent(size_t n) const {
        if (count_ == 0) return BSTError{"Empty buffer"};
        size_t take = std::min(n, count_);
        std::vector<InteractionEvent> result(take);
        for (size_t i = 0; i < take; ++i) {
            size_t idx = (head_ + capacity_ - take + i) % capacity_;
            result[i] = buffer_[idx];
        }
        return result;
    }

    OmniResult<std::vector<int64_t>> get_item_sequence(size_t max_len) const {
        auto recent = get_recent(max_len);
        if (auto* err = std::get_if<BSTError>(&recent)) return *err;
        auto& events = std::get<std::vector<InteractionEvent>>(recent);
        std::vector<int64_t> ids;
        ids.reserve(events.size());
        for (const auto& e : events) ids.push_back(e.item_id);
        return ids;
    }

    size_t size() const { return count_; }
    bool empty() const { return count_ == 0; }
    void clear() { head_ = 0; count_ = 0; }
};
