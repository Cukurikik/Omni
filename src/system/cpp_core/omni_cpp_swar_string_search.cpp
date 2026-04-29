// OMNI MOTHER — SEMESTER 14 BATCH 36
// C++ — System Layer (OMNI Zero-Mock Implementation)
// Implements production-grade SIMD-accelerated string search using SWAR technique.
// Absorbs patterns from: mischasan/aho-corasick, SIMD string processing papers

#include <cstdint>
#include <cstring>
#include <vector>
#include <string>

namespace omni {
namespace system {
namespace simd {

template <typename T>
struct Result {
    T value;
    std::string error;
    bool is_ok;
    static Result<T> Ok(T val) { return {val, "", true}; }
    static Result<T> Err(std::string err) { return {T{}, err, false}; }
};

struct SearchHit {
    size_t position;
    size_t pattern_length;
};

/**
 * SWAR (SIMD Within A Register) byte finder.
 *
 * Uses the classic bit-twiddling hack to find a specific byte
 * within a 64-bit word in O(1) operations:
 *   has_zero(v) = ((v - 0x0101...) & ~v & 0x8080...)
 *
 * This is the EXACT technique used by glibc's memchr and
 * musl's strlen implementations.
 *
 * @param word 8 bytes packed into a 64-bit integer
 * @param byte_val The byte value to search for
 * @return true if byte_val appears anywhere in the word
 */
inline bool swar_has_byte(uint64_t word, uint8_t byte_val) {
    // Broadcast byte to all 8 positions
    uint64_t broadcast = byte_val * 0x0101010101010101ULL;
    // XOR to zero matching bytes
    uint64_t xored = word ^ broadcast;
    // Classic zero-byte detection
    uint64_t has_zero = (xored - 0x0101010101010101ULL) & ~xored & 0x8080808080808080ULL;
    return has_zero != 0;
}

/**
 * Finds the position of a byte within a SWAR word.
 * Returns byte index (0-7) or -1 if not found.
 */
inline int swar_find_byte_position(uint64_t word, uint8_t byte_val) {
    uint64_t broadcast = byte_val * 0x0101010101010101ULL;
    uint64_t xored = word ^ broadcast;
    uint64_t has_zero = (xored - 0x0101010101010101ULL) & ~xored & 0x8080808080808080ULL;

    if (has_zero == 0) return -1;

    // Count trailing zeros to find position (little-endian)
    // Each matching byte has its high bit set in has_zero
    int pos = 0;
    uint64_t test = has_zero;
    while ((test & 0xFF) == 0) {
        test >>= 8;
        pos++;
    }
    return pos;
}

/**
 * Brute-force string search accelerated with SWAR first-byte filtering.
 *
 * Strategy:
 * 1. Use SWAR to quickly scan for the first byte of the pattern
 * 2. Only perform full memcmp at positions where first byte matches
 * 3. This reduces comparison count dramatically for long haystacks
 *
 * @param haystack The text to search in
 * @param haystack_len Length of haystack
 * @param needle The pattern to search for
 * @param needle_len Length of needle
 * @return All positions where needle occurs in haystack
 */
Result<std::vector<SearchHit>> swar_string_search(
    const uint8_t* haystack,
    size_t haystack_len,
    const uint8_t* needle,
    size_t needle_len
) {
    if (haystack == nullptr || needle == nullptr) {
        return Result<std::vector<SearchHit>>::Err("SWAR search: null pointer input.");
    }
    if (needle_len == 0) {
        return Result<std::vector<SearchHit>>::Err("SWAR search: empty needle.");
    }
    if (needle_len > haystack_len) {
        return Result<std::vector<SearchHit>>::Ok({});
    }

    std::vector<SearchHit> hits;
    const uint8_t first_byte = needle[0];
    const size_t search_end = haystack_len - needle_len + 1;

    size_t i = 0;

    // Process 8 bytes at a time using SWAR
    while (i + 8 <= search_end) {
        uint64_t word;
        memcpy(&word, &haystack[i], 8);

        if (swar_has_byte(word, first_byte)) {
            // First byte found in this word — check each position
            for (int j = 0; j < 8 && (i + j) < search_end; j++) {
                if (haystack[i + j] == first_byte) {
                    // Full pattern comparison
                    if (memcmp(&haystack[i + j], needle, needle_len) == 0) {
                        hits.push_back(SearchHit{i + static_cast<size_t>(j), needle_len});
                    }
                }
            }
        }

        i += 8;
    }

    // Handle remaining bytes (< 8)
    while (i < search_end) {
        if (haystack[i] == first_byte) {
            if (memcmp(&haystack[i], needle, needle_len) == 0) {
                hits.push_back(SearchHit{i, needle_len});
            }
        }
        i++;
    }

    return Result<std::vector<SearchHit>>::Ok(hits);
}

} // namespace simd
} // namespace system
} // namespace omni
