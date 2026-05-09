// omni_ring_buffer.cpp — Lock-Free Ring Buffer for Audio Streaming
// Inspired by: SoundStorm real-time audio pipeline
// Layer: System / C++
//
// SPSC (Single Producer Single Consumer) lock-free ring buffer
// for zero-copy audio sample transfer between codec and playback threads.

#ifndef OMNI_RING_BUFFER_HPP
#define OMNI_RING_BUFFER_HPP

#include <atomic>
#include <cstdint>
#include <cstring>
#include <algorithm>
#include <type_traits>

namespace omni {
namespace system {

/// Lock-free SPSC ring buffer with power-of-two sizing.
/// Suitable for real-time audio streaming between threads.
template <typename T, size_t Capacity>
class RingBuffer {
    static_assert((Capacity & (Capacity - 1)) == 0,
                  "Capacity must be a power of two");
    static_assert(std::is_trivially_copyable_v<T>,
                  "T must be trivially copyable for lock-free operation");

public:
    RingBuffer() : write_pos_(0), read_pos_(0) {
        std::memset(buffer_, 0, sizeof(buffer_));
    }

    /// Write a single element. Returns true on success.
    bool write(const T& value) noexcept {
        const size_t wp = write_pos_.load(std::memory_order_relaxed);
        const size_t rp = read_pos_.load(std::memory_order_acquire);

        if (available_write(wp, rp) == 0) {
            return false; // Full
        }

        buffer_[wp & kMask] = value;
        write_pos_.store(wp + 1, std::memory_order_release);
        return true;
    }

    /// Write multiple elements. Returns number of elements written.
    size_t write_bulk(const T* data, size_t count) noexcept {
        const size_t wp = write_pos_.load(std::memory_order_relaxed);
        const size_t rp = read_pos_.load(std::memory_order_acquire);
        const size_t available = available_write(wp, rp);
        const size_t to_write = std::min(count, available);

        if (to_write == 0) return 0;

        const size_t start = wp & kMask;
        const size_t first_chunk = std::min(to_write, Capacity - start);
        const size_t second_chunk = to_write - first_chunk;

        std::memcpy(&buffer_[start], data, first_chunk * sizeof(T));
        if (second_chunk > 0) {
            std::memcpy(&buffer_[0], data + first_chunk,
                       second_chunk * sizeof(T));
        }

        write_pos_.store(wp + to_write, std::memory_order_release);
        return to_write;
    }

    /// Read a single element. Returns true on success.
    bool read(T& value) noexcept {
        const size_t rp = read_pos_.load(std::memory_order_relaxed);
        const size_t wp = write_pos_.load(std::memory_order_acquire);

        if (available_read(wp, rp) == 0) {
            return false; // Empty
        }

        value = buffer_[rp & kMask];
        read_pos_.store(rp + 1, std::memory_order_release);
        return true;
    }

    /// Read multiple elements. Returns number of elements read.
    size_t read_bulk(T* data, size_t count) noexcept {
        const size_t rp = read_pos_.load(std::memory_order_relaxed);
        const size_t wp = write_pos_.load(std::memory_order_acquire);
        const size_t available = available_read(wp, rp);
        const size_t to_read = std::min(count, available);

        if (to_read == 0) return 0;

        const size_t start = rp & kMask;
        const size_t first_chunk = std::min(to_read, Capacity - start);
        const size_t second_chunk = to_read - first_chunk;

        std::memcpy(data, &buffer_[start], first_chunk * sizeof(T));
        if (second_chunk > 0) {
            std::memcpy(data + first_chunk, &buffer_[0],
                       second_chunk * sizeof(T));
        }

        read_pos_.store(rp + to_read, std::memory_order_release);
        return to_read;
    }

    /// Peek at element without consuming it.
    bool peek(T& value) const noexcept {
        const size_t rp = read_pos_.load(std::memory_order_relaxed);
        const size_t wp = write_pos_.load(std::memory_order_acquire);

        if (available_read(wp, rp) == 0) {
            return false;
        }

        value = buffer_[rp & kMask];
        return true;
    }

    /// Skip n elements from read position.
    size_t skip(size_t count) noexcept {
        const size_t rp = read_pos_.load(std::memory_order_relaxed);
        const size_t wp = write_pos_.load(std::memory_order_acquire);
        const size_t available = available_read(wp, rp);
        const size_t to_skip = std::min(count, available);

        read_pos_.store(rp + to_skip, std::memory_order_release);
        return to_skip;
    }

    /// Number of readable elements.
    size_t size() const noexcept {
        const size_t wp = write_pos_.load(std::memory_order_acquire);
        const size_t rp = read_pos_.load(std::memory_order_acquire);
        return available_read(wp, rp);
    }

    /// Number of writable slots.
    size_t space() const noexcept {
        const size_t wp = write_pos_.load(std::memory_order_acquire);
        const size_t rp = read_pos_.load(std::memory_order_acquire);
        return available_write(wp, rp);
    }

    bool empty() const noexcept { return size() == 0; }
    bool full() const noexcept { return space() == 0; }

    static constexpr size_t capacity() noexcept { return Capacity; }

    /// Reset to empty state. Only safe when no concurrent access.
    void reset() noexcept {
        write_pos_.store(0, std::memory_order_relaxed);
        read_pos_.store(0, std::memory_order_relaxed);
    }

private:
    static constexpr size_t kMask = Capacity - 1;

    static size_t available_read(size_t wp, size_t rp) noexcept {
        return wp - rp;
    }

    static size_t available_write(size_t wp, size_t rp) noexcept {
        return Capacity - (wp - rp);
    }

    alignas(64) T buffer_[Capacity];
    alignas(64) std::atomic<size_t> write_pos_;
    alignas(64) std::atomic<size_t> read_pos_;
};

/// Audio-specific ring buffer with sample rate metadata
template <size_t FrameCapacity = 8192>
class AudioRingBuffer {
public:
    AudioRingBuffer(int sample_rate = 16000, int channels = 1)
        : sample_rate_(sample_rate), channels_(channels),
          total_written_(0), total_read_(0) {}

    size_t write_frames(const float* frames, size_t num_frames) {
        size_t written = ring_.write_bulk(frames, num_frames * channels_);
        total_written_ += written / channels_;
        return written / channels_;
    }

    size_t read_frames(float* frames, size_t num_frames) {
        size_t read = ring_.read_bulk(frames, num_frames * channels_);
        total_read_ += read / channels_;
        return read / channels_;
    }

    size_t available_frames() const {
        return ring_.size() / channels_;
    }

    double buffered_duration_ms() const {
        return static_cast<double>(available_frames()) / sample_rate_ * 1000.0;
    }

    double total_duration_written_s() const {
        return static_cast<double>(total_written_) / sample_rate_;
    }

    int sample_rate() const { return sample_rate_; }
    int channels() const { return channels_; }
    bool empty() const { return ring_.empty(); }

    void reset() {
        ring_.reset();
        total_written_ = 0;
        total_read_ = 0;
    }

private:
    RingBuffer<float, FrameCapacity> ring_;
    int sample_rate_;
    int channels_;
    uint64_t total_written_;
    uint64_t total_read_;
};

} // namespace system
} // namespace omni

#endif // OMNI_RING_BUFFER_HPP
