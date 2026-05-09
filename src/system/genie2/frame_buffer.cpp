/// @omni-layer System | @omni-source lucidrains/genie2-pytorch | @omni-lang C++
/// @omni-description Frame buffer kernel: ring buffer for video frame
/// tokenization with double buffering and async write support.
#include <cstdint>
#include <cstring>
#include <vector>
#include <atomic>

namespace omni { namespace video {

class FrameBuffer {
    std::vector<uint32_t> buffer_;
    size_t capacity_;
    size_t tokens_per_frame_;
    std::atomic<size_t> write_pos_{0};
    std::atomic<size_t> read_pos_{0};
    std::atomic<size_t> frame_count_{0};

public:
    FrameBuffer(size_t max_frames, size_t tokens_per_frame)
        : capacity_(max_frames), tokens_per_frame_(tokens_per_frame),
          buffer_(max_frames * tokens_per_frame, 0) {}

    bool write_frame(const uint32_t* tokens, size_t n_tokens) {
        if (n_tokens != tokens_per_frame_) return false;
        size_t pos = write_pos_.load(std::memory_order_relaxed);
        size_t next = (pos + 1) % capacity_;
        if (next == read_pos_.load(std::memory_order_acquire)) return false; // full
        std::memcpy(buffer_.data() + pos * tokens_per_frame_, tokens, n_tokens * sizeof(uint32_t));
        write_pos_.store(next, std::memory_order_release);
        frame_count_.fetch_add(1, std::memory_order_relaxed);
        return true;
    }

    bool read_frame(uint32_t* out, size_t n_tokens) {
        if (n_tokens != tokens_per_frame_) return false;
        size_t pos = read_pos_.load(std::memory_order_relaxed);
        if (pos == write_pos_.load(std::memory_order_acquire)) return false; // empty
        std::memcpy(out, buffer_.data() + pos * tokens_per_frame_, n_tokens * sizeof(uint32_t));
        read_pos_.store((pos + 1) % capacity_, std::memory_order_release);
        return true;
    }

    size_t available() const {
        size_t w = write_pos_.load(std::memory_order_acquire);
        size_t r = read_pos_.load(std::memory_order_acquire);
        return (w >= r) ? (w - r) : (capacity_ - r + w);
    }

    size_t total_frames() const { return frame_count_.load(std::memory_order_relaxed); }
    size_t capacity() const { return capacity_; }
    size_t tokens_per_frame() const { return tokens_per_frame_; }

    void reset() {
        write_pos_.store(0, std::memory_order_relaxed);
        read_pos_.store(0, std::memory_order_relaxed);
        frame_count_.store(0, std::memory_order_relaxed);
    }
};

}} // namespace omni::video
