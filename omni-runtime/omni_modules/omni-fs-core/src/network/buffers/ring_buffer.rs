// ============================================================
// 🦀 OMNI-FS-CORE: Generic Ring Buffer (Zero-Copy I/O Streaming)
// ============================================================
// Struktur data inti untuk buffered I/O streaming di OMNI.
// Menggantikan Node.js internal `ReadableStream` buffer
// dengan alokasi stack-friendly dan zero-copy semantics.
// ============================================================

/// Ring Buffer generik dengan kapasitas tetap.
/// Digunakan untuk buffered read/write I/O di seluruh OMNI runtime.
pub struct RingBuffer<T> {
    buffer: Vec<Option<T>>,
    capacity: usize,
    head: usize,      // Posisi tulis berikutnya
    tail: usize,      // Posisi baca berikutnya
    count: usize,     // Jumlah elemen saat ini
}

impl<T: Clone> RingBuffer<T> {
    /// Membuat RingBuffer baru dengan kapasitas tertentu.
    /// Kapasitas minimum 1, akan di-clamp jika 0.
    pub fn new(capacity: usize) -> Self {
        let cap = capacity.max(1);
        let mut buffer = Vec::with_capacity(cap);
        for _ in 0..cap {
            buffer.push(None);
        }
        RingBuffer {
            buffer,
            capacity: cap,
            head: 0,
            tail: 0,
            count: 0,
        }
    }

    /// Menambahkan elemen ke buffer. 
    /// Mengembalikan `Err` jika buffer penuh.
    pub fn push(&mut self, item: T) -> Result<(), &'static str> {
        if self.count == self.capacity {
            return Err("RingBuffer penuh: tidak bisa push");
        }
        self.buffer[self.head] = Some(item);
        self.head = (self.head + 1) % self.capacity;
        self.count += 1;
        Ok(())
    }

    /// Menambahkan elemen, menimpa elemen tertua jika penuh.
    /// Berguna untuk logging/tracing di mana data lama bisa dibuang.
    pub fn push_overwrite(&mut self, item: T) {
        if self.count == self.capacity {
            // Buang elemen tertua
            self.tail = (self.tail + 1) % self.capacity;
            self.count -= 1;
        }
        self.buffer[self.head] = Some(item);
        self.head = (self.head + 1) % self.capacity;
        self.count += 1;
    }

    /// Mengambil dan menghapus elemen tertua dari buffer.
    /// Mengembalikan `None` jika buffer kosong.
    pub fn pop(&mut self) -> Option<T> {
        if self.count == 0 {
            return None;
        }
        let item = self.buffer[self.tail].take();
        self.tail = (self.tail + 1) % self.capacity;
        self.count -= 1;
        item
    }

    /// Mengintip elemen tertua tanpa menghapusnya.
    pub fn peek(&self) -> Option<&T> {
        if self.count == 0 {
            return None;
        }
        self.buffer[self.tail].as_ref()
    }

    /// Menguras seluruh isi buffer ke dalam Vec.
    pub fn drain(&mut self) -> Vec<T> {
        let mut result = Vec::with_capacity(self.count);
        while let Some(item) = self.pop() {
            result.push(item);
        }
        result
    }

    /// Jumlah elemen yang ada di dalam buffer saat ini.
    pub fn len(&self) -> usize {
        self.count
    }

    /// Apakah buffer kosong?
    pub fn is_empty(&self) -> bool {
        self.count == 0
    }

    /// Apakah buffer penuh?
    pub fn is_full(&self) -> bool {
        self.count == self.capacity
    }

    /// Kapasitas maksimum buffer.
    pub fn capacity(&self) -> usize {
        self.capacity
    }

    /// Sisa ruang yang tersedia.
    pub fn available(&self) -> usize {
        self.capacity - self.count
    }

    /// Mengosongkan seluruh buffer tanpa mengubah kapasitas.
    pub fn clear(&mut self) {
        for slot in self.buffer.iter_mut() {
            *slot = None;
        }
        self.head = 0;
        self.tail = 0;
        self.count = 0;
    }
}

// ============================================================
// Unit Tests
// ============================================================

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_push_pop() {
        let mut rb = RingBuffer::new(3);
        
        assert!(rb.push(10).is_ok());
        assert!(rb.push(20).is_ok());
        assert!(rb.push(30).is_ok());
        assert!(rb.push(40).is_err()); // Penuh!
        
        assert_eq!(rb.pop(), Some(10));
        assert_eq!(rb.pop(), Some(20));
        assert_eq!(rb.pop(), Some(30));
        assert_eq!(rb.pop(), None); // Kosong!
    }

    #[test]
    fn test_overwrite_mode() {
        let mut rb = RingBuffer::new(2);
        rb.push_overwrite(1);
        rb.push_overwrite(2);
        rb.push_overwrite(3); // Menimpa 1
        
        assert_eq!(rb.pop(), Some(2));
        assert_eq!(rb.pop(), Some(3));
    }

    #[test]
    fn test_drain() {
        let mut rb = RingBuffer::new(4);
        rb.push(100).ok();
        rb.push(200).ok();
        rb.push(300).ok();
        
        let drained = rb.drain();
        assert_eq!(drained, vec![100, 200, 300]);
        assert!(rb.is_empty());
    }

    #[test]
    fn test_peek() {
        let mut rb = RingBuffer::new(2);
        rb.push(42).ok();
        assert_eq!(rb.peek(), Some(&42));
        assert_eq!(rb.len(), 1); // Peek tidak menghapus
    }

    #[test]
    fn test_capacity_and_available() {
        let mut rb: RingBuffer<u8> = RingBuffer::new(5);
        assert_eq!(rb.capacity(), 5);
        assert_eq!(rb.available(), 5);
        
        rb.push(1).ok();
        rb.push(2).ok();
        assert_eq!(rb.available(), 3);
    }
}
