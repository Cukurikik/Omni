/*
 * omni_memory_pool.cpp — Fixed-Block Memory Pool
 * Layer: System / C++
 *
 * Implements a template-based memory pool for allocating objects of the 
 * same size without the overhead of standard new/delete. Ensures contiguous
 * memory and minimizes heap fragmentation. Zero mock.
 */

#include <vector>
#include <cstdint>
#include <mutex>
#include <stdexcept>

template <typename T, size_t BlockSize = 4096>
class OmniMemoryPool {
private:
    union Slot {
        T element;
        Slot* next;
    };

    Slot* currentBlock_;
    Slot* currentSlot_;
    Slot* lastSlot_;
    Slot* freeSlots_;
    
    std::mutex mutex_;
    std::vector<Slot*> allocatedBlocks_;

    void allocateBlock() {
        Slot* newBlock = reinterpret_cast<Slot*>(operator new(BlockSize * sizeof(Slot)));
        allocatedBlocks_.push_back(newBlock);
        
        currentBlock_ = newBlock;
        currentSlot_ = currentBlock_;
        lastSlot_ = currentBlock_ + BlockSize - 1;
        
        // Link slots for the free list if needed, or rely on bump-pointer
        // For bump-pointer fast path:
        currentSlot_->next = nullptr; 
    }

public:
    OmniMemoryPool() : currentBlock_(nullptr), currentSlot_(nullptr), lastSlot_(nullptr), freeSlots_(nullptr) {
        allocateBlock();
    }

    ~OmniMemoryPool() {
        for (Slot* block : allocatedBlocks_) {
            operator delete(reinterpret_cast<void*>(block));
        }
    }

    // Prohibit copy
    OmniMemoryPool(const OmniMemoryPool&) = delete;
    OmniMemoryPool& operator=(const OmniMemoryPool&) = delete;

    template <typename... Args>
    T* allocate(Args&&... args) {
        std::lock_guard<std::mutex> lock(mutex_);
        
        Slot* slot = nullptr;
        
        if (freeSlots_ != nullptr) {
            slot = freeSlots_;
            freeSlots_ = freeSlots_->next;
        } else {
            if (currentSlot_ >= lastSlot_) {
                allocateBlock();
            }
            slot = currentSlot_++;
        }
        
        // Placement new
        return new (reinterpret_cast<T*>(slot)) T(std::forward<Args>(args)...);
    }

    void deallocate(T* p) {
        if (p != nullptr) {
            std::lock_guard<std::mutex> lock(mutex_);
            
            p->~T(); // Call destructor manually
            
            Slot* slot = reinterpret_cast<Slot*>(p);
            slot->next = freeSlots_;
            freeSlots_ = slot;
        }
    }
};
