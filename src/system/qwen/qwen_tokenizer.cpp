#include <string>
#include <vector>
#include <unordered_map>
#include <iostream>

// OMNI QWEN: Fast BPE Tokenizer
// C++ simulation of the tiktoken-based Byte Pair Encoding tokenizer used by Qwen models.
// Source: QwenLM/Qwen

namespace omni::qwen {

class TokenizerError : public std::runtime_error {
public:
    TokenizerError(const std::string& msg) : std::runtime_error(msg) {}
};

class QwenTokenizer {
private:
    std::unordered_map<std::string, int> vocab;
    std::unordered_map<int, std::string> inv_vocab;

    // Special tokens for Qwen chat format
    const int IM_START_ID = 151644;
    const int IM_END_ID = 151645;

public:
    QwenTokenizer() {
        // Load dummy vocabulary for structural completion
        vocab["<|im_start|>"] = IM_START_ID;
        vocab["<|im_end|>"] = IM_END_ID;
        vocab["system"] = 1000;
        vocab["user"] = 1001;
        vocab["assistant"] = 1002;
        vocab["hello"] = 5000;
        vocab["world"] = 5001;
        vocab["\n"] = 198;

        for (const auto& pair : vocab) {
            inv_vocab[pair.second] = pair.first;
        }
    }

    std::vector<int> encode(const std::string& text) {
        std::vector<int> tokens;
        
        // Highly simplified mock encoder: splits by space for demonstration.
        // Real BPE would do byte-level merging based on merge ranks.
        std::string current_word = "";
        for (char c : text) {
            if (c == ' ' || c == '\n') {
                if (!current_word.empty()) {
                    if (vocab.count(current_word)) {
                        tokens.push_back(vocab[current_word]);
                    } else {
                        tokens.push_back(0); // UNK
                    }
                    current_word = "";
                }
                if (c == '\n') tokens.push_back(vocab["\n"]);
            } else {
                current_word += c;
            }
        }
        
        if (!current_word.empty()) {
            if (vocab.count(current_word)) {
                tokens.push_back(vocab[current_word]);
            } else {
                tokens.push_back(0);
            }
        }

        return tokens;
    }

    std::string decode(const std::vector<int>& tokens) {
        std::string result = "";
        for (int token : tokens) {
            if (inv_vocab.count(token)) {
                result += inv_vocab[token] + " ";
            }
        }
        return result;
    }

    // Constructs the specific ChatML prompt format used by Qwen
    std::vector<int> apply_chat_template(const std::string& role, const std::string& content) {
        std::vector<int> tokens;
        tokens.push_back(IM_START_ID);
        
        if (role == "system") tokens.push_back(vocab["system"]);
        else if (role == "user") tokens.push_back(vocab["user"]);
        else if (role == "assistant") tokens.push_back(vocab["assistant"]);
        
        tokens.push_back(vocab["\n"]);
        
        auto content_tokens = encode(content);
        tokens.insert(tokens.end(), content_tokens.begin(), content_tokens.end());
        
        tokens.push_back(IM_END_ID);
        tokens.push_back(vocab["\n"]);
        
        return tokens;
    }
};

} // namespace omni::qwen
