// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Meta Llama3 Tokenizer (OMNI Zero-Mock Implementation)
// Implements Byte-Pair Encoding logic for sequence separation

#include <vector>
#include <string>
#include <unordered_map>

namespace omni {
namespace compute {
namespace llama3 {

template <typename T>
struct Result {
    T value;
    std::string error;
    bool is_ok;
    
    static Result<T> Ok(T val) { return {val, "", true}; }
    static Result<T> Err(std::string err) { return {T(), err, false}; }
};

struct BPEMerge {
    std::string token1;
    std::string token2;
    int rank;
};

class Llama3BPETokenizer {
private:
    std::unordered_map<std::string, int> vocab;
    std::vector<BPEMerge> merges;

public:
    void register_merge(std::string t1, std::string t2, int rank) {
        merges.push_back({t1, t2, rank});
    }

    Result<std::vector<std::string>> encode(const std::string& word) {
        if (word.empty()) {
            return Result<std::vector<std::string>>::Err("Input word cannot be empty.");
        }

        std::vector<std::string> symbols;
        for (char c : word) {
            symbols.push_back(std::string(1, c));
        }

        while (true) {
            if (symbols.size() < 2) break;

            int best_rank = 999999;
            int best_idx = -1;

            for (size_t i = 0; i < symbols.size() - 1; ++i) {
                for (const auto& merge : merges) {
                    if (symbols[i] == merge.token1 && symbols[i+1] == merge.token2) {
                        if (merge.rank < best_rank) {
                            best_rank = merge.rank;
                            best_idx = i;
                        }
                    }
                }
            }

            if (best_idx == -1) break; // No more merges possible

            std::vector<std::string> new_symbols;
            for (size_t i = 0; i < symbols.size(); ++i) {
                if (static_cast<int>(i) == best_idx) {
                    new_symbols.push_back(symbols[i] + symbols[i+1]);
                    i++; // Skip the next symbol as it's merged
                } else {
                    new_symbols.push_back(symbols[i]);
                }
            }
            symbols = new_symbols;
        }

        return Result<std::vector<std::string>>::Ok(symbols);
    }
};

} // namespace llama3
} // namespace compute
} // namespace omni
