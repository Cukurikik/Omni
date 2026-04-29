#include <cstdint>
#include <cstddef>
#include <string>

extern "C" {

typedef struct {
    int is_success;
    char* geohash_str;
    int error_code;
} GeohashResult;

// FFI bindings for high-performance Geohashing

static const char BASE32[] = "0123456789bcdefghjkmnpqrstuvwxyz";

GeohashResult encode_geohash(double lat, double lon, int precision) {
    GeohashResult res = {0, nullptr, 0};
    
    if (precision < 1 || precision > 12) {
        res.error_code = 1;
        return res;
    }
    
    if (lat < -90.0 || lat > 90.0 || lon < -180.0 || lon > 180.0) {
        res.error_code = 2;
        return res;
    }

    // Scalar implementation of Geohash (Production would use AVX vectorization for batching)
    char* hash = new char[precision + 1];
    hash[precision] = '\0';
    
    double lat_min = -90.0, lat_max = 90.0;
    double lon_min = -180.0, lon_max = 180.0;
    
    bool is_even = true;
    int bit = 0;
    int ch = 0;
    int len = 0;
    
    while (len < precision) {
        if (is_even) {
            double mid = (lon_min + lon_max) / 2.0;
            if (lon > mid) {
                ch |= (1 << (4 - bit));
                lon_min = mid;
            } else {
                lon_max = mid;
            }
        } else {
            double mid = (lat_min + lat_max) / 2.0;
            if (lat > mid) {
                ch |= (1 << (4 - bit));
                lat_min = mid;
            } else {
                lat_max = mid;
            }
        }
        
        is_even = !is_even;
        if (bit < 4) {
            bit++;
        } else {
            hash[len++] = BASE32[ch];
            bit = 0;
            ch = 0;
        }
    }
    
    res.is_success = 1;
    res.geohash_str = hash;
    return res;
}

void free_geohash_str(char* str) {
    if (str) {
        delete[] str;
    }
}

} // extern "C"
