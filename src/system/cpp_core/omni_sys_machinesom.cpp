#include <cstdint>

extern "C" {
    int omni_sys_machinesom_conflict_resolution(int* votes, int size) {
        if (!votes || size <= 0) return -1;
        
        int majority_vote = votes[0];
        int count = 1;
        
        // Boyer-Moore Majority Vote Algorithm
        for (int i = 1; i < size; i++) {
            if (votes[i] == majority_vote) {
                count++;
            } else {
                count--;
                if (count == 0) {
                    majority_vote = votes[i];
                    count = 1;
                }
            }
        }
        return majority_vote;
    }
}
