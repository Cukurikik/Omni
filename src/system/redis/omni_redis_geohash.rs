// OMNI Redis GeoHash Engine — System Layer (Rust)
// Absorbing redis/redis geo location radius structures
// Deterministic geohashing algorithm conversion geometry

use std::collections::HashMap;

#[derive(Debug)]
pub enum GeoError {
    BoundsException,
}

type Result<T> = std::result::Result<T, GeoError>;

pub struct OmniRedisGeohash {
    hashes_encoded: u64,
}

impl OmniRedisGeohash {
    pub fn new() -> Self {
        Self { hashes_encoded: 0 }
    }

    /// Evaluates structural geohash 52-bit exact float map into GeoHash string coordinate
    /// Standard Base32 encoding for latitude/longitude interleaving.
    pub fn encode_coordinates(
        &mut self,
        latitude: f64,
        longitude: f64,
        precision: usize
    ) -> Result<String> {
        if latitude < -90.0 || latitude > 90.0 || longitude < -180.0 || longitude > 180.0 {
            return Err(GeoError::BoundsException);
        }
        if precision == 0 || precision > 12 {
            return Err(GeoError::BoundsException);
        }

        self.hashes_encoded += 1;

        let base32_chars = "0123456789bcdefghjkmnpqrstuvwxyz".as_bytes();
        let mut is_even = true;
        let mut lat_range = (-90.0, 90.0);
        let mut lon_range = (-180.0, 180.0);
        
        let mut geohash = String::with_capacity(precision);
        let mut bit = 0;
        let mut ch = 0;

        while geohash.len() < precision {
            let mid;
            if is_even {
                mid = (lon_range.0 + lon_range.1) / 2.0;
                if longitude >= mid {
                    ch |= 1 << (4 - bit);
                    lon_range.0 = mid;
                } else {
                    lon_range.1 = mid;
                }
            } else {
                mid = (lat_range.0 + lat_range.1) / 2.0;
                if latitude >= mid {
                    ch |= 1 << (4 - bit);
                    lat_range.0 = mid;
                } else {
                    lat_range.1 = mid;
                }
            }

            is_even = !is_even;
            if bit < 4 {
                bit += 1;
            } else {
                geohash.push(base32_chars[ch] as char);
                bit = 0;
                ch = 0;
            }
        }

        Ok(geohash)
    }

    pub fn diagnostics(&self) -> HashMap<String, String> {
        let mut map = HashMap::new();
        map.insert("engine".to_string(), "OmniRedisGeohash".to_string());
        map.insert("hashes_encoded".to_string(), self.hashes_encoded.to_string());
        map.insert("status".to_string(), "Operational".to_string());
        map
    }
}
