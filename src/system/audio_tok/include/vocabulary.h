#pragma once
#ifndef OMNI_AUDIO_TOK_VOCABULARY_H
#define OMNI_AUDIO_TOK_VOCABULARY_H

#include <unordered_map>
#include <string>
#include <vector>
#include <stdexcept>

namespace omni {
namespace audio {

class VocabularyError : public std::runtime_error {
public:
    explicit VocabularyError(const std::string& msg) : std::runtime_error(msg) {}
};

class Vocabulary {
public:
    Vocabulary() = default;
    
    void load_from_file(const std::string& filepath);
    void save_to_file(const std::string& filepath) const;
    
    int token_to_id(const std::string& token) const;
    std::string id_to_token(int id) const;
    
    void add_token(const std::string& token);
    size_t size() const;

private:
    std::unordered_map<std::string, int> _token_to_id;
    std::unordered_map<int, std::string> _id_to_token;
    int _next_id = 0;
};

} // namespace audio
} // namespace omni

#endif // OMNI_AUDIO_TOK_VOCABULARY_H
