#include "vocabulary.h"
#include <fstream>
#include <iostream>

namespace omni {
namespace audio {

void Vocabulary::load_from_file(const std::string& filepath) {
    std::ifstream infile(filepath);
    if (!infile.is_open()) {
        throw VocabularyError("Failed to open vocabulary file for reading: " + filepath);
    }
    
    std::string token;
    int id;
    while (infile >> token >> id) {
        _token_to_id[token] = id;
        _id_to_token[id] = token;
        if (id >= _next_id) {
            _next_id = id + 1;
        }
    }
}

void Vocabulary::save_to_file(const std::string& filepath) const {
    std::ofstream outfile(filepath);
    if (!outfile.is_open()) {
        throw VocabularyError("Failed to open vocabulary file for writing: " + filepath);
    }
    
    for (const auto& pair : _token_to_id) {
        outfile << pair.first << " " << pair.second << "\n";
    }
}

int Vocabulary::token_to_id(const std::string& token) const {
    auto it = _token_to_id.find(token);
    if (it != _token_to_id.end()) {
        return it->second;
    }
    return -1; // Unknown token
}

std::string Vocabulary::id_to_token(int id) const {
    auto it = _id_to_token.find(id);
    if (it != _id_to_token.end()) {
        return it->second;
    }
    return "[UNK]";
}

void Vocabulary::add_token(const std::string& token) {
    if (_token_to_id.find(token) == _token_to_id.end()) {
        _token_to_id[token] = _next_id;
        _id_to_token[_next_id] = token;
        _next_id++;
    }
}

size_t Vocabulary::size() const {
    return _token_to_id.size();
}

} // namespace audio
} // namespace omni
