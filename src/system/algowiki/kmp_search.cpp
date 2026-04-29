#include <vector>
#include <string>

// OMNI ALGOWIKI: Knuth-Morris-Pratt (KMP) Substring Search
// Linear time string matching algorithm.
// Source: vicky002/AlgoWiki

namespace omni::algowiki {

enum class SearchError {
    SUCCESS,
    EMPTY_PATTERN,
    PATTERN_TOO_LONG
};

template <typename T>
struct SearchResult {
    T index;
    SearchError error;
    bool is_ok() const { return error == SearchError::SUCCESS; }
};

// Computes the Longest Prefix Suffix (LPS) array
std::vector<int> compute_lps(const std::string& pattern) {
    int m = pattern.length();
    std::vector<int> lps(m, 0);
    int len = 0;
    int i = 1;

    while (i < m) {
        if (pattern[i] == pattern[len]) {
            len++;
            lps[i] = len;
            i++;
        } else {
            if (len != 0) {
                len = lps[len - 1];
            } else {
                lps[i] = 0;
                i++;
            }
        }
    }
    return lps;
}

SearchResult<int> kmp_search(const std::string& text, const std::string& pattern) {
    if (pattern.empty()) {
        return {-1, SearchError::EMPTY_PATTERN};
    }
    
    int n = text.length();
    int m = pattern.length();
    
    if (m > n) {
        return {-1, SearchError::SUCCESS}; // Pattern longer than text, naturally not found
    }

    std::vector<int> lps = compute_lps(pattern);
    
    int i = 0; // index for text
    int j = 0; // index for pattern
    
    while (i < n) {
        if (pattern[j] == text[i]) {
            j++;
            i++;
        }
        
        if (j == m) {
            // Match found, return the starting index
            return {i - j, SearchError::SUCCESS};
        } else if (i < n && pattern[j] != text[i]) {
            if (j != 0) {
                j = lps[j - 1];
            } else {
                i++;
            }
        }
    }
    
    // Not found
    return {-1, SearchError::SUCCESS};
}

} // namespace omni::algowiki
