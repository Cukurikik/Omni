#include <unordered_map>
#include <list>
#include <string>

namespace OmniCache {
    class LRUCache {
        size_t capacity;
        std::list<std::pair<std::string, std::string>> items;
        std::unordered_map<std::string, decltype(items.begin())> map;
    public:
        LRUCache(size_t cap) : capacity(cap) {}
        void put(const std::string& key, const std::string& val) {
            // implementation
        }
    };
}
