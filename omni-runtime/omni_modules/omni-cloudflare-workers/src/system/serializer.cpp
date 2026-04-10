#include <string>
#include <vector>
#include <cstring>
#include <cstdint>

namespace omni_cloudflare_workers {

class BinarySerializer {
    std::vector<uint8_t> buffer_;
public:
    void write_u8(uint8_t v) { buffer_.push_back(v); }
    void write_u16(uint16_t v) { write_u8(v & 0xFF); write_u8((v >> 8) & 0xFF); }
    void write_u32(uint32_t v) { write_u16(v & 0xFFFF); write_u16((v >> 16) & 0xFFFF); }
    void write_u64(uint64_t v) { write_u32(v & 0xFFFFFFFF); write_u32((v >> 32) & 0xFFFFFFFF); }
    void write_bytes(const uint8_t* data, size_t len) { write_u32((uint32_t)len); buffer_.insert(buffer_.end(), data, data + len); }
    void write_string(const std::string& s) { write_bytes((const uint8_t*)s.data(), s.size()); }
    const std::vector<uint8_t>& data() const { return buffer_; }
    size_t size() const { return buffer_.size(); }
    void clear() { buffer_.clear(); }
};

class BinaryDeserializer {
    const uint8_t* data_; size_t len_; size_t pos_;
public:
    BinaryDeserializer(const uint8_t* d, size_t l) : data_(d), len_(l), pos_(0) {}
    uint8_t read_u8() { return data_[pos_++]; }
    uint16_t read_u16() { uint16_t v = read_u8(); v |= ((uint16_t)read_u8() << 8); return v; }
    uint32_t read_u32() { uint32_t v = read_u16(); v |= ((uint32_t)read_u16() << 16); return v; }
    uint64_t read_u64() { uint64_t v = read_u32(); v |= ((uint64_t)read_u32() << 32); return v; }
    std::vector<uint8_t> read_bytes() { uint32_t l = read_u32(); std::vector<uint8_t> b(data_ + pos_, data_ + pos_ + l); pos_ += l; return b; }
    std::string read_string() { auto b = read_bytes(); return std::string(b.begin(), b.end()); }
    bool has_more() const { return pos_ < len_; }
};

} // namespace