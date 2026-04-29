#include <cstdint>
#include <cstddef>

extern "C" {

typedef struct {
    int is_success;
    uint8_t* payload;
    size_t length;
    uint32_t src_ip;
    uint32_t dst_ip;
    uint16_t src_port;
    uint16_t dst_port;
    uint8_t protocol;
    int error_code;
} PacketCaptureResult;

// FFI bindings for AF_PACKET / libpcap for high-speed zero-copy packet capture

PacketCaptureResult read_next_packet(void* pcap_handle) {
    PacketCaptureResult res = {0, nullptr, 0, 0, 0, 0, 0, 0, 0};
    
    if (!pcap_handle) {
        res.error_code = 1; // Invalid handle
        return res;
    }

    // In a real scenario: pcap_next_ex(handle, &header, &data);
    // Structural FFI simulation returning a dummy IPv4 TCP packet
    size_t dummy_len = 64;
    uint8_t* dummy_data = new uint8_t[dummy_len];
    
    // Fill with zeroes, just structural
    for (size_t i=0; i<dummy_len; i++) dummy_data[i] = 0;

    res.is_success = 1;
    res.payload = dummy_data;
    res.length = dummy_len;
    
    // Network byte order simulated (e.g. 192.168.1.1 -> 10.0.0.1)
    res.src_ip = 0xC0A80101; 
    res.dst_ip = 0x0A000001;
    res.src_port = 443;
    res.dst_port = 54321;
    res.protocol = 6; // TCP
    
    return res;
}

void free_packet_payload(uint8_t* payload) {
    if (payload) {
        delete[] payload;
    }
}

} // extern "C"
