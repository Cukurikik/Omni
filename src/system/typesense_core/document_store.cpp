#include <omni/result.hpp>
#include <string>
#include <unordered_map>

namespace omni::typesense {

class DocumentStore {
    std::unordered_map<std::string, std::string> store;
public:
    omni::Result<bool, std::string> upsert(const std::string& id, const std::string& doc) {
        if (id.empty()) return omni::Err<std::string>("ID cannot be empty");
        store[id] = doc;
        return omni::Ok(true);
    }
};

}
