// ============================================================
// 🦀 OMNI-BUFFER: Rust Native Binary Buffer
// ============================================================
#![allow(dead_code)]
// Pengganti total Node.js `Buffer` dengan zero-copy semantics,
// endianness control, dan safe slice operations.
// ============================================================

use std::fmt;

/// OmniBuffer — binary data container yang aman dan efisien.
/// Menggantikan Node.js Buffer dengan API Rusty.
pub struct OmniBuffer {
    data: Vec<u8>,
    position: usize,
}

impl OmniBuffer {
    /// Membuat buffer kosong dengan kapasitas tertentu.
    /// Ekuivalen Node.js: `Buffer.alloc(size)`
    pub fn alloc(size: usize) -> Self {
        OmniBuffer {
            data: vec![0u8; size],
            position: 0,
        }
    }

    /// Membuat buffer dari slice byte yang ada.
    /// Ekuivalen Node.js: `Buffer.from(data)`
    pub fn from_bytes(bytes: &[u8]) -> Self {
        OmniBuffer {
            data: bytes.to_vec(),
            position: 0,
        }
    }

    /// Membuat buffer dari string UTF-8.
    /// Ekuivalen Node.js: `Buffer.from(str, 'utf-8')`
    pub fn from_string(s: &str) -> Self {
        Self::from_bytes(s.as_bytes())
    }

    /// Ukuran buffer dalam bytes.
    /// Ekuivalen Node.js: `buf.length`
    pub fn len(&self) -> usize {
        self.data.len()
    }

    pub fn is_empty(&self) -> bool {
        self.data.is_empty()
    }

    /// Akses byte pada posisi tertentu.
    pub fn get(&self, index: usize) -> Option<u8> {
        self.data.get(index).copied()
    }

    /// Set byte pada posisi tertentu.
    pub fn set(&mut self, index: usize, value: u8) -> bool {
        if index < self.data.len() {
            self.data[index] = value;
            true
        } else {
            false
        }
    }

    // ============================================================
    // Operasi Baca (Little-Endian & Big-Endian)
    // ============================================================

    /// Baca unsigned 16-bit integer (little-endian).
    pub fn read_u16_le(&self, offset: usize) -> Option<u16> {
        if offset + 2 > self.data.len() { return None; }
        Some(u16::from_le_bytes([self.data[offset], self.data[offset + 1]]))
    }

    /// Baca unsigned 16-bit integer (big-endian).
    pub fn read_u16_be(&self, offset: usize) -> Option<u16> {
        if offset + 2 > self.data.len() { return None; }
        Some(u16::from_be_bytes([self.data[offset], self.data[offset + 1]]))
    }

    /// Baca unsigned 32-bit integer (little-endian).
    pub fn read_u32_le(&self, offset: usize) -> Option<u32> {
        if offset + 4 > self.data.len() { return None; }
        let bytes: [u8; 4] = [
            self.data[offset], self.data[offset+1],
            self.data[offset+2], self.data[offset+3],
        ];
        Some(u32::from_le_bytes(bytes))
    }

    /// Baca unsigned 32-bit integer (big-endian).
    pub fn read_u32_be(&self, offset: usize) -> Option<u32> {
        if offset + 4 > self.data.len() { return None; }
        let bytes: [u8; 4] = [
            self.data[offset], self.data[offset+1],
            self.data[offset+2], self.data[offset+3],
        ];
        Some(u32::from_be_bytes(bytes))
    }

    /// Baca 64-bit float (little-endian).
    pub fn read_f64_le(&self, offset: usize) -> Option<f64> {
        if offset + 8 > self.data.len() { return None; }
        let mut bytes = [0u8; 8];
        bytes.copy_from_slice(&self.data[offset..offset + 8]);
        Some(f64::from_le_bytes(bytes))
    }

    // ============================================================
    // Operasi Tulis
    // ============================================================

    /// Tulis unsigned 16-bit integer (little-endian).
    pub fn write_u16_le(&mut self, offset: usize, value: u16) -> bool {
        if offset + 2 > self.data.len() { return false; }
        let bytes = value.to_le_bytes();
        self.data[offset] = bytes[0];
        self.data[offset + 1] = bytes[1];
        true
    }

    /// Tulis unsigned 32-bit integer (little-endian).
    pub fn write_u32_le(&mut self, offset: usize, value: u32) -> bool {
        if offset + 4 > self.data.len() { return false; }
        let bytes = value.to_le_bytes();
        for i in 0..4 { self.data[offset + i] = bytes[i]; }
        true
    }

    // ============================================================
    // Operasi Slice & Copy
    // ============================================================

    /// Mengambil sub-slice dari buffer.
    /// Ekuivalen Node.js: `buf.subarray(start, end)`
    pub fn slice(&self, start: usize, end: usize) -> OmniBuffer {
        let s = start.min(self.data.len());
        let e = end.min(self.data.len());
        OmniBuffer::from_bytes(&self.data[s..e])
    }

    /// Menyalin data dari buffer lain ke posisi tertentu.
    /// Ekuivalen Node.js: `source.copy(target, targetStart)`
    pub fn copy_from(&mut self, source: &OmniBuffer, target_start: usize) -> usize {
        let available = self.data.len().saturating_sub(target_start);
        let count = source.len().min(available);
        self.data[target_start..target_start + count]
            .copy_from_slice(&source.data[..count]);
        count
    }

    /// Menggabungkan dua buffer menjadi satu buffer baru.
    /// Ekuivalen Node.js: `Buffer.concat([buf1, buf2])`
    pub fn concat(a: &OmniBuffer, b: &OmniBuffer) -> OmniBuffer {
        let mut result = Vec::with_capacity(a.len() + b.len());
        result.extend_from_slice(&a.data);
        result.extend_from_slice(&b.data);
        OmniBuffer { data: result, position: 0 }
    }

    /// Mengisi seluruh buffer dengan nilai tertentu.
    /// Ekuivalen Node.js: `buf.fill(value)`
    pub fn fill(&mut self, value: u8) {
        for byte in self.data.iter_mut() {
            *byte = value;
        }
    }

    /// Konversi ke string UTF-8.
    /// Ekuivalen Node.js: `buf.toString('utf-8')`
    pub fn to_string_utf8(&self) -> String {
        String::from_utf8_lossy(&self.data).into_owned()
    }

    /// Konversi ke hex string.
    /// Ekuivalen Node.js: `buf.toString('hex')`
    pub fn to_hex(&self) -> String {
        self.data.iter().map(|b| format!("{:02x}", b)).collect()
    }

    /// Membandingkan dua buffer.
    /// Ekuivalen Node.js: `buf.equals(other)`
    pub fn equals(&self, other: &OmniBuffer) -> bool {
        self.data == other.data
    }

    /// Mencari byte pertama yang cocok.
    /// Ekuivalen Node.js: `buf.indexOf(value)`
    pub fn index_of(&self, value: u8) -> Option<usize> {
        self.data.iter().position(|&b| b == value)
    }

    /// Akses raw pointer (untuk FFI zero-copy).
    pub fn as_ptr(&self) -> *const u8 {
        self.data.as_ptr()
    }

    /// Akses raw slice.
    pub fn as_bytes(&self) -> &[u8] {
        &self.data
    }
}

impl fmt::Debug for OmniBuffer {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "<OmniBuffer len={} hex={}>", self.len(),
            if self.len() <= 16 { self.to_hex() } else {
                format!("{}...", &self.to_hex()[..32])
            }
        )
    }
}

// ============================================================
// Unit Tests
// ============================================================

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_alloc_and_fill() {
        let mut buf = OmniBuffer::alloc(8);
        assert_eq!(buf.len(), 8);
        buf.fill(0xFF);
        assert_eq!(buf.get(0), Some(0xFF));
        assert_eq!(buf.get(7), Some(0xFF));
    }

    #[test]
    fn test_from_string_and_back() {
        let buf = OmniBuffer::from_string("OMNI");
        assert_eq!(buf.to_string_utf8(), "OMNI");
        assert_eq!(buf.to_hex(), "4f4d4e49");
    }

    #[test]
    fn test_read_write_integers() {
        let mut buf = OmniBuffer::alloc(8);
        buf.write_u16_le(0, 0x1234);
        assert_eq!(buf.read_u16_le(0), Some(0x1234));

        buf.write_u32_le(4, 0xDEADBEEF);
        assert_eq!(buf.read_u32_le(4), Some(0xDEADBEEF));
    }

    #[test]
    fn test_slice_and_concat() {
        let full = OmniBuffer::from_bytes(&[1, 2, 3, 4, 5]);
        let part = full.slice(1, 4);
        assert_eq!(part.as_bytes(), &[2, 3, 4]);

        let a = OmniBuffer::from_bytes(&[10, 20]);
        let b = OmniBuffer::from_bytes(&[30, 40]);
        let merged = OmniBuffer::concat(&a, &b);
        assert_eq!(merged.as_bytes(), &[10, 20, 30, 40]);
    }

    #[test]
    fn test_index_of() {
        let buf = OmniBuffer::from_bytes(&[0, 1, 2, 3, 4]);
        assert_eq!(buf.index_of(3), Some(3));
        assert_eq!(buf.index_of(99), None);
    }
}
