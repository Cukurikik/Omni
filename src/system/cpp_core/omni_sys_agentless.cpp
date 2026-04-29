#include <cstring>

extern "C" {
    /// Score a candidate patch location by line proximity to fault.
    float omni_sys_agentless_location_score(int fault_line, int candidate_line, int file_len) {
        if (file_len <= 0) return 0.0f;
        int dist = (fault_line > candidate_line) ? fault_line - candidate_line : candidate_line - fault_line;
        return 1.0f - ((float)dist / (float)file_len);
    }

    /// Validate a diff hunk header format (@@...@@).
    int omni_sys_agentless_valid_hunk(const char* hunk, int len) {
        if (!hunk || len < 4) return 0;
        return (hunk[0] == '@' && hunk[1] == '@' && hunk[len-1] == '@' && hunk[len-2] == '@') ? 1 : 0;
    }
}
