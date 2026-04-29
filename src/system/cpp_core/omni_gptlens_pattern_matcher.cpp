// Omni GPTLens Solidity Pattern Matcher (C++)
// Ref: git-disl/GPTLens — TPS'23
#include <string>
#include <vector>
struct VulnFinding { int line; std::string type; std::string snippet; float confidence; };
std::vector<VulnFinding> omni_scan_reentrancy(const std::string& src) {
    std::vector<VulnFinding> results;
    size_t pos = 0; int line = 1;
    while (pos < src.size()) {
        size_t nl = src.find('\n', pos);
        std::string ln = src.substr(pos, (nl == std::string::npos ? src.size() : nl) - pos);
        if (ln.find(".call{value:") != std::string::npos) {
            results.push_back({line, "reentrancy", ln.substr(0, 80), 0.85f});
        }
        if (ln.find("tx.origin") != std::string::npos) {
            results.push_back({line, "tx_origin", ln.substr(0, 80), 0.90f});
        }
        pos = (nl == std::string::npos) ? src.size() : nl + 1;
        line++;
    }
    return results;
}
