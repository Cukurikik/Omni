#include <unordered_map>
#include <list>
#include <string>
#include <mutex>
#include <chrono>
#include <vector>

namespace omni_mariadb {

template<typename K, typename V>
class LRUCache {
    size_t capacity_;
    std::list<std::pair<K, V>> items_;
    std::unordered_map<K, typename std::list<std::pair<K, V>>::iterator> map_;
    std::mutex mtx_;
    uint64_t hits_ = 0, misses_ = 0;
public:
    LRUCache(size_t cap) : capacity_(cap) {}
    void put(const K& key, const V& val) {
        std::lock_guard<std::mutex> lock(mtx_);
        auto it = map_.find(key);
        if (it != map_.end()) { items_.erase(it->second); }
        items_.push_front({key, val});
        map_[key] = items_.begin();
        while (items_.size() > capacity_) { map_.erase(items_.back().first); items_.pop_back(); }
    }
    bool get(const K& key, V& val) {
        std::lock_guard<std::mutex> lock(mtx_);
        auto it = map_.find(key);
        if (it == map_.end()) { misses_++; return false; }
        items_.splice(items_.begin(), items_, it->second);
        val = it->second->second;
        hits_++; return true;
    }
    void evict(const K& key) { std::lock_guard<std::mutex> lock(mtx_); auto it = map_.find(key); if (it != map_.end()) { items_.erase(it->second); map_.erase(it); } }
    void clear() { std::lock_guard<std::mutex> lock(mtx_); items_.clear(); map_.clear(); }
    size_t size() { std::lock_guard<std::mutex> lock(mtx_); return items_.size(); }
    double hit_rate() { return (hits_ + misses_) > 0 ? (double)hits_ / (hits_ + misses_) : 0.0; }
};

} // namespace