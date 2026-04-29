#include <cstring>

extern "C" {
    int omni_sys_genome_gc_content(const char* sequence) {
        if (!sequence) return 0;
        
        int gc_count = 0;
        int total = 0;
        
        for (int i = 0; sequence[i] != '\0'; ++i) {
            char c = sequence[i];
            if (c == 'G' || c == 'C' || c == 'g' || c == 'c') {
                gc_count++;
            }
            total++;
        }
        
        if (total == 0) return 0;
        return (gc_count * 100) / total; // Integer percentage
    }
}
