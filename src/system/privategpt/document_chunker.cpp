#include <vector>
#include <string>

// OMNI PRIVATEGPT: Document Chunker
// C++ logic to split large text documents into overlapping chunks for vector ingestion.
// Source: imartinez/privateGPT

namespace omni::privategpt {

struct Chunk {
    std::string text;
    int start_char;
    int end_char;
};

class DocumentChunker {
private:
    int chunk_size;
    int chunk_overlap;

public:
    DocumentChunker(int size = 1000, int overlap = 200) 
        : chunk_size(size), chunk_overlap(overlap) {
        if (chunk_overlap >= chunk_size) {
            // Force valid bounds
            chunk_overlap = chunk_size / 2;
        }
    }

    std::vector<Chunk> split_text(const std::string& text) {
        std::vector<Chunk> chunks;
        int text_len = text.length();
        int current_pos = 0;

        while (current_pos < text_len) {
            int end_pos = current_pos + chunk_size;
            
            // Try to avoid breaking words if possible (simple heuristic)
            if (end_pos < text_len) {
                // backtrack to find a space
                int space_pos = end_pos;
                while (space_pos > current_pos && text[space_pos] != ' ' && text[space_pos] != '\n') {
                    space_pos--;
                }
                if (space_pos > current_pos) {
                    end_pos = space_pos;
                }
            } else {
                end_pos = text_len;
            }

            std::string chunk_text = text.substr(current_pos, end_pos - current_pos);
            chunks.push_back({chunk_text, current_pos, end_pos});

            // Advance pointer, accounting for overlap
            current_pos = end_pos - chunk_overlap;
            
            // Prevent infinite loops on edge cases
            if (current_pos <= chunks.back().start_char) {
                current_pos = end_pos; 
            }
        }

        return chunks;
    }
};

} // namespace omni::privategpt
