#include <fstream>
#include <string>
#include <iostream>

// OMNI STANFORD ALPACA: JSONL Dataset Writer
// C++ fast IO writer to rapidly append generated instruction-tuning pairs to a JSONL file.
// Source: tatsu-lab/stanford_alpaca

namespace omni::alpaca {

enum class WriterError {
    SUCCESS,
    FILE_OPEN_FAILED,
    WRITE_FAILED
};

template<typename T>
struct Result {
    T value;
    WriterError error;
    bool is_ok() const { return error == WriterError::SUCCESS; }
};

struct InstructionPair {
    std::string instruction;
    std::string input;
    std::string output;
};

class JsonlWriter {
private:
    std::ofstream file;

    // Helper to escape JSON strings simply
    std::string escape_json(const std::string& s) {
        std::string res;
        for (char c : s) {
            if (c == '"') res += "\\\"";
            else if (c == '\\') res += "\\\\";
            else if (c == '\n') res += "\\n";
            else if (c == '\r') res += "\\r";
            else if (c == '\t') res += "\\t";
            else res += c;
        }
        return res;
    }

public:
    JsonlWriter(const std::string& filepath) {
        // Open in append mode
        file.open(filepath, std::ios::out | std::ios::app);
    }

    ~JsonlWriter() {
        if (file.is_open()) {
            file.close();
        }
    }

    Result<bool> write_pair(const InstructionPair& pair) {
        if (!file.is_open()) {
            return {false, WriterError::FILE_OPEN_FAILED};
        }

        std::string json = "{";
        json += "\"instruction\":\"" + escape_json(pair.instruction) + "\",";
        json += "\"input\":\"" + escape_json(pair.input) + "\",";
        json += "\"output\":\"" + escape_json(pair.output) + "\"";
        json += "}\n";

        file << json;

        if (file.fail()) {
            return {false, WriterError::WRITE_FAILED};
        }

        return {true, WriterError::SUCCESS};
    }

    void flush() {
        if (file.is_open()) {
            file.flush();
        }
    }
};

} // namespace omni::alpaca
