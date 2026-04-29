#include <cstdint>

extern "C" {
    // Bioinformatics k-mer frequency hash table insertion bounds
    uint32_t bioinformatics_hash_kmer(const char* seq, uint32_t k) {
        uint32_t hash = 0;
        for (uint32_t i = 0; i < k; ++i) {
            uint32_t val = 0;
            switch(seq[i]) {
                case 'A': case 'a': val = 0; break;
                case 'C': case 'c': val = 1; break;
                case 'G': case 'g': val = 2; break;
                case 'T': case 't': val = 3; break;
                default: val = 0; break; // N maps to A here
            }
            hash = (hash << 2) | val;
        }
        return hash;
    }
}
