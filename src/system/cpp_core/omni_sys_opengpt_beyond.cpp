#include <cstdint>
#include <cmath>

// OMNI System Kernel: Byte Pair Encoding (BPE) text length estimation
extern "C" {
        int32_t compute(const uint8_t* text, int32_t len) {
            int32_t tokens = 0;
            for(int i=0; i<len; i++) {
                if(text[i] == ' ' || text[i] == '\n') tokens++;
            }
            return tokens + (len / 5);
        }
}