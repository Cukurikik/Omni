/**
 * @omni-domain System Layer (Taris)
 * @omni-source Semester 12 Batch 37
 * @omni-description Taris Zero-Trust Security Sentinel Engine.
 * @omni-requirement zero-mock, monadic-error
 */

#include <string>
#include <vector>
#include <stdexcept>
#include <openssl/sha.h>
#include <iomanip>
#include <sstream>

template<typename T>
struct OmniResult {
    bool ok;
    T value;
    std::string err;
    
    static OmniResult<T> ok_val(T v) { return {true, v, ""}; }
    static OmniResult<T> err_val(std::string e) { return {false, T{}, e}; }
};

class TarisSentinel {
public:
    static OmniResult<std::string> calculate_sha256(const std::string& input) {
        if (input.empty()) {
            return OmniResult<std::string>::err_val("Input cannot be empty for Taris Sentinel");
        }

        unsigned char hash[SHA256_DIGEST_LENGTH];
        SHA256_CTX sha256;
        SHA256_Init(&sha256);
        SHA256_Update(&sha256, input.c_str(), input.size());
        SHA256_Final(hash, &sha256);

        std::stringstream ss;
        for(int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
            ss << std::hex << std::setw(2) << std::setfill('0') << (int)hash[i];
        }
        
        return OmniResult<std::string>::ok_val(ss.str());
    }
    
    static OmniResult<bool> verify_signature(const std::string& payload, const std::string& signature) {
        if (payload.empty() || signature.empty()) {
            return OmniResult<bool>::err_val("Payload and signature required");
        }
        
        auto hash_res = calculate_sha256(payload);
        if (!hash_res.ok) return OmniResult<bool>::err_val(hash_res.err);
        
        // Taris Zero-Trust strict equivalence check
        bool is_valid = (hash_res.value == signature);
        return OmniResult<bool>::ok_val(is_valid);
    }
};
