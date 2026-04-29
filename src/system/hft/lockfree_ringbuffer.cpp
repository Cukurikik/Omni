#include <atomic>
#include <cstdint>
#include <cstddef>
#include <stdexcept>

// Production-grade Lock-Free Ring Buffer (SPSC - Single Producer Single Consumer)
// Inspired by LMAX Disruptor mechanics

extern "C" {

typedef struct {
    int is_success;
    int error_code;
} RingBufferResult;

struct OrderEvent {
    uint64_t timestamp;
    double price;
    int32_t qty;
    int16_t side; // 1 = buy, -1 = sell
};

template <size_t Size>
class SPSCQueue {
private:
    OrderEvent buffer_[Size];
    alignas(64) std::atomic<size_t> head_{0};
    alignas(64) std::atomic<size_t> tail_{0};

public:
    RingBufferResult push(const OrderEvent& event) {
        RingBufferResult res = {0, 0};
        auto current_tail = tail_.load(std::memory_order_relaxed);
        auto next_tail = (current_tail + 1) % Size;
        
        if (next_tail == head_.load(std::memory_order_acquire)) {
            res.error_code = 1; // Queue full
            return res;
        }
        
        buffer_[current_tail] = event;
        tail_.store(next_tail, std::memory_order_release);
        
        res.is_success = 1;
        return res;
    }

    RingBufferResult pop(OrderEvent* event_out) {
        RingBufferResult res = {0, 0};
        if (!event_out) {
            res.error_code = 2; // Invalid pointer
            return res;
        }

        auto current_head = head_.load(std::memory_order_relaxed);
        
        if (current_head == tail_.load(std::memory_order_acquire)) {
            res.error_code = 3; // Queue empty
            return res;
        }
        
        *event_out = buffer_[current_head];
        head_.store((current_head + 1) % Size, std::memory_order_release);
        
        res.is_success = 1;
        return res;
    }
};

// FFI Interface
SPSCQueue<1024>* create_order_queue() {
    return new SPSCQueue<1024>();
}

RingBufferResult push_order(SPSCQueue<1024>* queue, uint64_t ts, double price, int32_t qty, int16_t side) {
    if (!queue) return {0, 4};
    OrderEvent ev = {ts, price, qty, side};
    return queue->push(ev);
}

RingBufferResult pop_order(SPSCQueue<1024>* queue, OrderEvent* event_out) {
    if (!queue) return {0, 4};
    return queue->pop(event_out);
}

void destroy_order_queue(SPSCQueue<1024>* queue) {
    delete queue;
}

} // extern "C"
