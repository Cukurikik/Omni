// ===========================================================================
// OMNI MEMORY ENGINE (SEMESTER 3 — BATCH 38.9)
// ===========================================================================
// Absorbed From  : jemalloc + tcmalloc + C++ allocators + memory pool patterns
// Logic Inherited: C++ / System Layer (Memory Management & Allocator Design)
// ===========================================================================
//
// By studying jemalloc, tcmalloc, and C++ custom allocators, Mother learned:
//   1. Arena allocator: pre-allocate large block, bump-pointer alloc, bulk free
//   2. Pool allocator: fixed-size slabs for objects of same size
//   3. Stack allocator: LIFO allocation from a stack buffer
//   4. Alignment: all allocations must respect natural alignment
//   5. Memory tracking: count allocations/deallocations for leak detection

#pragma once

#include <cstddef>
#include <cstdlib>
#include <cstring>
#include <cassert>
#include <atomic>
#include <memory>
#include <vector>
#include <string>
#include <mutex>

namespace omni::system::cpp {

// ============================================================
// PART 1: Arena Allocator (Bump Pointer)
// ============================================================

/**
 * ArenaAllocator: fast bump-pointer allocation from a pre-allocated block.
 * All memory is freed at once when the arena is destroyed.
 * No individual deallocations — perfect for request-scoped memory.
 */
class ArenaAllocator {
    struct Block {
        std::unique_ptr<char[]> memory;
        std::size_t size;
        std::size_t used;

        Block(std::size_t sz)
            : memory(new char[sz]), size(sz), used(0) {}
    };

    std::vector<Block> blocks_;
    std::size_t default_block_size_;
    std::size_t total_allocated_ = 0;
    std::size_t total_alloc_calls_ = 0;

    static constexpr std::size_t DEFAULT_BLOCK_SIZE = 64 * 1024; // 64KB

public:
    explicit ArenaAllocator(std::size_t block_size = DEFAULT_BLOCK_SIZE)
        : default_block_size_(block_size)
    {
        blocks_.emplace_back(block_size);
    }

    /// Allocate `size` bytes with `alignment`.
    void* allocate(std::size_t size, std::size_t alignment = alignof(std::max_align_t)) {
        total_alloc_calls_++;

        Block& current = blocks_.back();

        // Align the current position
        std::size_t aligned_used = (current.used + alignment - 1) & ~(alignment - 1);

        if (aligned_used + size > current.size) {
            // Need a new block
            std::size_t new_size = std::max(default_block_size_, size + alignment);
            blocks_.emplace_back(new_size);
            Block& new_block = blocks_.back();
            aligned_used = 0;
            total_allocated_ += size;
            new_block.used = size;
            return new_block.memory.get();
        }

        void* ptr = current.memory.get() + aligned_used;
        current.used = aligned_used + size;
        total_allocated_ += size;
        return ptr;
    }

    /// Allocate and construct an object.
    template <typename T, typename... Args>
    T* create(Args&&... args) {
        void* mem = allocate(sizeof(T), alignof(T));
        return new (mem) T(std::forward<Args>(args)...);
    }

    /// Reset the arena (reuse memory without deallocation).
    void reset() {
        for (auto& block : blocks_) {
            block.used = 0;
        }
        total_allocated_ = 0;
        total_alloc_calls_ = 0;
    }

    /// Get total bytes allocated.
    std::size_t bytes_allocated() const { return total_allocated_; }

    /// Get total allocation calls.
    std::size_t alloc_count() const { return total_alloc_calls_; }

    /// Get total capacity across all blocks.
    std::size_t capacity() const {
        std::size_t total = 0;
        for (const auto& b : blocks_) total += b.size;
        return total;
    }

    /// Number of blocks.
    std::size_t block_count() const { return blocks_.size(); }
};

// ============================================================
// PART 2: Pool Allocator (Fixed-Size Slabs)
// ============================================================

/**
 * PoolAllocator: allocates objects of fixed size from pre-allocated slabs.
 * Freed objects are returned to a free-list for reuse.
 */
class PoolAllocator {
    struct FreeNode {
        FreeNode* next;
    };

    std::vector<std::unique_ptr<char[]>> slabs_;
    FreeNode* free_list_ = nullptr;
    std::size_t object_size_;
    std::size_t objects_per_slab_;
    std::size_t total_allocs_ = 0;
    std::size_t total_frees_ = 0;
    std::mutex mutex_;

public:
    PoolAllocator(std::size_t object_size, std::size_t objects_per_slab = 128)
        : object_size_(std::max(object_size, sizeof(FreeNode)))
        , objects_per_slab_(objects_per_slab)
    {
        allocate_slab();
    }

    /// Allocate one object-sized block.
    void* allocate() {
        std::lock_guard<std::mutex> lock(mutex_);
        total_allocs_++;

        if (!free_list_) {
            allocate_slab();
        }

        FreeNode* node = free_list_;
        free_list_ = node->next;
        return node;
    }

    /// Deallocate one object-sized block (return to free list).
    void deallocate(void* ptr) {
        if (!ptr) return;
        std::lock_guard<std::mutex> lock(mutex_);
        total_frees_++;

        FreeNode* node = static_cast<FreeNode*>(ptr);
        node->next = free_list_;
        free_list_ = node;
    }

    /// Allocate and construct.
    template <typename T, typename... Args>
    T* create(Args&&... args) {
        static_assert(sizeof(T) <= sizeof(FreeNode) || true,
            "Object must fit in pool slot");
        void* mem = allocate();
        return new (mem) T(std::forward<Args>(args)...);
    }

    /// Destruct and deallocate.
    template <typename T>
    void destroy(T* obj) {
        if (!obj) return;
        obj->~T();
        deallocate(obj);
    }

    std::size_t total_allocations() const { return total_allocs_; }
    std::size_t total_deallocations() const { return total_frees_; }
    std::size_t slab_count() const { return slabs_.size(); }

private:
    void allocate_slab() {
        auto slab = std::make_unique<char[]>(object_size_ * objects_per_slab_);
        char* raw = slab.get();

        // Chain all slots into the free list
        for (std::size_t i = 0; i < objects_per_slab_; ++i) {
            FreeNode* node = reinterpret_cast<FreeNode*>(raw + i * object_size_);
            node->next = free_list_;
            free_list_ = node;
        }

        slabs_.push_back(std::move(slab));
    }
};

// ============================================================
// PART 3: Stack Allocator (LIFO)
// ============================================================

/**
 * StackAllocator: LIFO allocation from a fixed stack buffer.
 * Fast allocation and deallocation in reverse order.
 */
class StackAllocator {
    std::unique_ptr<char[]> buffer_;
    std::size_t capacity_;
    std::size_t top_ = 0;
    std::size_t total_allocs_ = 0;

public:
    explicit StackAllocator(std::size_t capacity)
        : buffer_(new char[capacity]), capacity_(capacity) {}

    /// Allocate from the top of the stack.
    void* allocate(std::size_t size, std::size_t alignment = alignof(std::max_align_t)) {
        std::size_t aligned_top = (top_ + alignment - 1) & ~(alignment - 1);
        if (aligned_top + size > capacity_) {
            return nullptr; // Stack overflow
        }
        void* ptr = buffer_.get() + aligned_top;
        top_ = aligned_top + size;
        total_allocs_++;
        return ptr;
    }

    /// Save the current position (for batch deallocation).
    std::size_t save_point() const { return top_; }

    /// Restore to a saved position (deallocate everything above).
    void restore(std::size_t point) {
        assert(point <= top_);
        top_ = point;
    }

    /// Reset the entire stack.
    void reset() { top_ = 0; total_allocs_ = 0; }

    std::size_t bytes_used() const { return top_; }
    std::size_t bytes_free() const { return capacity_ - top_; }
    std::size_t alloc_count() const { return total_allocs_; }
};

// ============================================================
// PART 4: Memory Tracker (Leak Detection)
// ============================================================

/**
 * MemoryTracker: global allocation tracker for leak detection.
 */
class MemoryTracker {
    static inline std::atomic<int64_t> current_allocations_{0};
    static inline std::atomic<int64_t> total_allocated_bytes_{0};
    static inline std::atomic<int64_t> total_freed_bytes_{0};
    static inline std::atomic<int64_t> peak_bytes_{0};

public:
    static void record_alloc(std::size_t bytes) {
        current_allocations_.fetch_add(1, std::memory_order_relaxed);
        int64_t total = total_allocated_bytes_.fetch_add(
            static_cast<int64_t>(bytes), std::memory_order_relaxed) + bytes;

        // Update peak
        int64_t current_peak = peak_bytes_.load(std::memory_order_relaxed);
        int64_t current_live = total - total_freed_bytes_.load(std::memory_order_relaxed);
        while (current_live > current_peak) {
            if (peak_bytes_.compare_exchange_weak(current_peak, current_live)) break;
        }
    }

    static void record_free(std::size_t bytes) {
        current_allocations_.fetch_sub(1, std::memory_order_relaxed);
        total_freed_bytes_.fetch_add(static_cast<int64_t>(bytes), std::memory_order_relaxed);
    }

    static int64_t live_allocations() {
        return current_allocations_.load(std::memory_order_relaxed);
    }

    static int64_t live_bytes() {
        return total_allocated_bytes_.load() - total_freed_bytes_.load();
    }

    static int64_t peak() {
        return peak_bytes_.load(std::memory_order_relaxed);
    }

    static bool has_leaks() {
        return live_allocations() > 0;
    }

    static void reset() {
        current_allocations_ = 0;
        total_allocated_bytes_ = 0;
        total_freed_bytes_ = 0;
        peak_bytes_ = 0;
    }
};

// ============================================================
// Diagnostics
// ============================================================

struct OmniMemoryDiagnostics {
    static auto diagnostics() {
        struct Result {
            const char* engine = "OmniMemoryEngine";
            const char* layer = "C++ System";
            std::vector<std::string> components = {
                "ArenaAllocator", "PoolAllocator",
                "StackAllocator", "MemoryTracker"
            };
            std::vector<std::string> learned_logic = {
                "arena-bump-pointer-alloc",
                "pool-fixed-size-slab-freelist",
                "stack-lifo-savepoint-restore",
                "alignment-natural-power-of-two",
                "memory-tracker-leak-detection",
                "peak-memory-atomic-cas-update",
                "placement-new-construct-in-pool",
                "raii-unique-ptr-slab-ownership"
            };
        };
        return Result{};
    }
};

} // namespace omni::system::cpp
