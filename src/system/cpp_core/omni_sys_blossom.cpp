#include <cstdint>

// Simplified Bloom filter structure for dataset deduplication
class BlossomBloomFilter {
private:
    uint8_t* bit_array;
    uint32_t size_in_bytes;

    uint32_t hash1(const char* data, uint32_t len) {
        uint32_t hash = 5381;
        for (uint32_t i = 0; i < len; ++i) hash = ((hash << 5) + hash) + data[i];
        return hash;
    }

    uint32_t hash2(const char* data, uint32_t len) {
        uint32_t hash = 0;
        for (uint32_t i = 0; i < len; ++i) hash = data[i] + (hash << 6) + (hash << 16) - hash;
        return hash;
    }

public:
    BlossomBloomFilter(uint8_t* mem, uint32_t size) : bit_array(mem), size_in_bytes(size) {}

    void add(const char* data, uint32_t len) {
        if (size_in_bytes == 0) return;
        uint32_t bit_size = size_in_bytes * 8;
        uint32_t h1 = hash1(data, len) % bit_size;
        uint32_t h2 = hash2(data, len) % bit_size;
        
        bit_array[h1 / 8] |= (1 << (h1 % 8));
        bit_array[h2 / 8] |= (1 << (h2 % 8));
    }

    bool might_contain(const char* data, uint32_t len) {
        if (size_in_bytes == 0) return false;
        uint32_t bit_size = size_in_bytes * 8;
        uint32_t h1 = hash1(data, len) % bit_size;
        uint32_t h2 = hash2(data, len) % bit_size;
        
        bool check1 = (bit_array[h1 / 8] & (1 << (h1 % 8))) != 0;
        bool check2 = (bit_array[h2 / 8] & (1 << (h2 % 8))) != 0;
        
        return check1 && check2;
    }
};

extern "C" {
    void blossom_add_to_filter(uint8_t* filter_mem, uint32_t filter_size, const char* data, uint32_t len) {
        BlossomBloomFilter bf(filter_mem, filter_size);
        bf.add(data, len);
    }
    
    bool blossom_check_filter(uint8_t* filter_mem, uint32_t filter_size, const char* data, uint32_t len) {
        BlossomBloomFilter bf(filter_mem, filter_size);
        return bf.might_contain(data, len);
    }
}
