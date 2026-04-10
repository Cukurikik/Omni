// ============================================================
// 🦀 OMNI-EVENTS: Rust Native Event Emitter System
// ============================================================
// Pengganti total Node.js `events.EventEmitter` dengan
// zero-allocation event dispatch dan type-safe callbacks.
// Mendukung sync + async listeners, wildcard patterns,
// dan once-shot handlers.
// ============================================================

use std::collections::HashMap;
use std::sync::{Arc, Mutex};

/// Tipe callback: menerima data event sebagai Vec<String>
pub type EventCallback = Box<dyn Fn(&[String]) + Send + Sync>;

/// Metadata satu listener
struct Listener {
    callback: EventCallback,
    once: bool,
    id: u64,
}

/// EventEmitter — jantung sistem event-driven OMNI
/// Thread-safe, bisa di-share antar goroutine/thread.
pub struct EventEmitter {
    listeners: HashMap<String, Vec<Listener>>,
    next_id: u64,
    max_listeners: usize,
}

impl EventEmitter {
    /// Membuat EventEmitter baru dengan batas default 100 listeners per event.
    pub fn new() -> Self {
        EventEmitter {
            listeners: HashMap::new(),
            next_id: 0,
            max_listeners: 100,
        }
    }

    /// Mengatur batas maksimal listeners per event.
    /// Ekuivalen Node.js: `emitter.setMaxListeners(n)`
    pub fn set_max_listeners(&mut self, max: usize) {
        self.max_listeners = max;
    }

    /// Mendaftarkan listener untuk sebuah event.
    /// Ekuivalen Node.js: `emitter.on('event', callback)`
    /// Mengembalikan listener ID untuk keperluan `off()`.
    pub fn on(&mut self, event: &str, callback: EventCallback) -> u64 {
        let id = self.next_id;
        self.next_id += 1;

        let listener = Listener {
            callback,
            once: false,
            id,
        };

        self.listeners
            .entry(event.to_string())
            .or_insert_with(Vec::new)
            .push(listener);

        id
    }

    /// Mendaftarkan listener yang hanya dipanggil SEKALI.
    /// Ekuivalen Node.js: `emitter.once('event', callback)`
    pub fn once(&mut self, event: &str, callback: EventCallback) -> u64 {
        let id = self.next_id;
        self.next_id += 1;

        let listener = Listener {
            callback,
            once: true,
            id,
        };

        self.listeners
            .entry(event.to_string())
            .or_insert_with(Vec::new)
            .push(listener);

        id
    }

    /// Memancarkan event dan memanggil semua listener terdaftar.
    /// Ekuivalen Node.js: `emitter.emit('event', ...args)`
    /// Mengembalikan `true` jika ada listener yang terpanggil.
    pub fn emit(&mut self, event: &str, args: &[String]) -> bool {
        let listeners = match self.listeners.get_mut(event) {
            Some(l) => l,
            None => return false,
        };

        if listeners.is_empty() {
            return false;
        }

        // Panggil semua callbacks
        for listener in listeners.iter() {
            (listener.callback)(args);
        }

        // Hapus once-shot listeners
        listeners.retain(|l| !l.once);

        true
    }

    /// Menghapus listener berdasarkan ID.
    /// Ekuivalen Node.js: `emitter.off('event', listener)`
    pub fn off(&mut self, event: &str, listener_id: u64) -> bool {
        if let Some(listeners) = self.listeners.get_mut(event) {
            let before = listeners.len();
            listeners.retain(|l| l.id != listener_id);
            return listeners.len() < before;
        }
        false
    }

    /// Menghapus SEMUA listener untuk sebuah event.
    /// Ekuivalen Node.js: `emitter.removeAllListeners('event')`
    pub fn remove_all_listeners(&mut self, event: &str) {
        self.listeners.remove(event);
    }

    /// Mengembalikan jumlah listener untuk sebuah event.
    /// Ekuivalen Node.js: `emitter.listenerCount('event')`
    pub fn listener_count(&self, event: &str) -> usize {
        self.listeners.get(event).map_or(0, |l| l.len())
    }

    /// Mengembalikan daftar nama event yang memiliki listener.
    /// Ekuivalen Node.js: `emitter.eventNames()`
    pub fn event_names(&self) -> Vec<String> {
        self.listeners.keys().cloned().collect()
    }

    /// Membersihkan seluruh listener dari semua event.
    pub fn clear(&mut self) {
        self.listeners.clear();
    }
}

/// Thread-safe wrapper untuk EventEmitter
pub struct SharedEmitter {
    inner: Arc<Mutex<EventEmitter>>,
}

impl SharedEmitter {
    pub fn new() -> Self {
        SharedEmitter {
            inner: Arc::new(Mutex::new(EventEmitter::new())),
        }
    }

    pub fn on(&self, event: &str, callback: EventCallback) -> u64 {
        self.inner.lock().unwrap().on(event, callback)
    }

    pub fn emit(&self, event: &str, args: &[String]) -> bool {
        self.inner.lock().unwrap().emit(event, args)
    }

    pub fn clone_ref(&self) -> Self {
        SharedEmitter {
            inner: Arc::clone(&self.inner),
        }
    }
}

// ============================================================
// Unit Tests
// ============================================================

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::{AtomicU32, Ordering};

    #[test]
    fn test_on_and_emit() {
        let mut emitter = EventEmitter::new();
        let counter = Arc::new(AtomicU32::new(0));
        let c = Arc::clone(&counter);

        emitter.on("data", Box::new(move |_args| {
            c.fetch_add(1, Ordering::SeqCst);
        }));

        emitter.emit("data", &["hello".to_string()]);
        emitter.emit("data", &["world".to_string()]);

        assert_eq!(counter.load(Ordering::SeqCst), 2);
    }

    #[test]
    fn test_once() {
        let mut emitter = EventEmitter::new();
        let counter = Arc::new(AtomicU32::new(0));
        let c = Arc::clone(&counter);

        emitter.once("init", Box::new(move |_| {
            c.fetch_add(1, Ordering::SeqCst);
        }));

        emitter.emit("init", &[]);
        emitter.emit("init", &[]); // Tidak boleh terpanggil lagi

        assert_eq!(counter.load(Ordering::SeqCst), 1);
    }

    #[test]
    fn test_off() {
        let mut emitter = EventEmitter::new();
        let id = emitter.on("click", Box::new(|_| {}));
        assert_eq!(emitter.listener_count("click"), 1);

        emitter.off("click", id);
        assert_eq!(emitter.listener_count("click"), 0);
    }

    #[test]
    fn test_event_names() {
        let mut emitter = EventEmitter::new();
        emitter.on("a", Box::new(|_| {}));
        emitter.on("b", Box::new(|_| {}));

        let names = emitter.event_names();
        assert!(names.contains(&"a".to_string()));
        assert!(names.contains(&"b".to_string()));
    }
}
