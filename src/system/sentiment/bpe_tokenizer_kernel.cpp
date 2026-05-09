/// @omni-layer System | @omni-source TheophileBlard/french-sentiment | @omni-lang C++
/// @omni-description Tokenizer kernel: BPE merge operations with hash-based
/// vocabulary lookup and fast subword segmentation for multilingual text.
#include <cstdint>
#include <string>
#include <vector>
#include <unordered_map>
#include <algorithm>

namespace omni { namespace tokenizer {

struct MergePair {
    std::string left;
    std::string right;
    int priority;
};

class BPETokenizer {
    std::unordered_map<std::string, uint32_t> vocab_;
    std::vector<MergePair> merges_;
    uint32_t unk_id_;
    uint32_t pad_id_;

public:
    BPETokenizer(uint32_t unk_id = 0, uint32_t pad_id = 1)
        : unk_id_(unk_id), pad_id_(pad_id) {}

    void add_vocab(const std::string& token, uint32_t id) {
        vocab_[token] = id;
    }

    void add_merge(const std::string& left, const std::string& right, int priority) {
        merges_.push_back({left, right, priority});
    }

    std::vector<std::string> pre_tokenize(const std::string& text) const {
        std::vector<std::string> tokens;
        std::string current;
        for (char c : text) {
            if (c == ' ' && !current.empty()) {
                tokens.push_back(current);
                current.clear();
            } else if (c != ' ') {
                current += c;
            }
        }
        if (!current.empty()) tokens.push_back(current);
        return tokens;
    }

    std::vector<std::string> bpe_segment(const std::string& word) const {
        std::vector<std::string> symbols;
        for (char c : word) symbols.push_back(std::string(1, c));

        for (const auto& merge : merges_) {
            for (size_t i = 0; i + 1 < symbols.size(); ) {
                if (symbols[i] == merge.left && symbols[i+1] == merge.right) {
                    symbols[i] = merge.left + merge.right;
                    symbols.erase(symbols.begin() + static_cast<long>(i) + 1);
                } else {
                    i++;
                }
            }
        }
        return symbols;
    }

    std::vector<uint32_t> encode(const std::string& text) const {
        auto words = pre_tokenize(text);
        std::vector<uint32_t> ids;
        for (const auto& word : words) {
            auto subwords = bpe_segment(word);
            for (const auto& sw : subwords) {
                auto it = vocab_.find(sw);
                ids.push_back(it != vocab_.end() ? it->second : unk_id_);
            }
        }
        return ids;
    }

    std::vector<uint32_t> pad(const std::vector<uint32_t>& ids, size_t max_len) const {
        auto result = ids;
        while (result.size() < max_len) result.push_back(pad_id_);
        if (result.size() > max_len) result.resize(max_len);
        return result;
    }

    size_t vocab_size() const { return vocab_.size(); }
    size_t merge_count() const { return merges_.size(); }
};

}} // namespace omni::tokenizer
