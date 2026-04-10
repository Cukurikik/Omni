use std::sync::atomic::{AtomicUsize, Ordering};
use std::collections::HashMap;
use std::sync::Mutex;

use std::sync::OnceLock;

/// 🧠 OMNI UNIVERSAL MEMORY ORCHESTRATOR
/// 
/// Ini adalah "Wasit" (Referee) untuk semua siklus memori bahasa.
/// Mencegah segfault ketika objek Garbage Collector Node V8 
/// mencoba dilempar ke Rust Ownership atau C++ manual Malloc.
///
/// Mekanisme: DRC (Distributed Reference Counting) lintas bahasa.
pub struct MemoryOrchestrator {
    /// Peta pointer (sebagai representasi u64) dengan Reference-Count (RC) global.
    global_refs: Mutex<HashMap<usize, AtomicUsize>>,
}

/// Singleton untuk Global Orchestrator Lintas Bahasa
pub static ORCHESTRATOR: OnceLock<MemoryOrchestrator> = OnceLock::new();

pub fn get_orchestrator() -> &'static MemoryOrchestrator {
    ORCHESTRATOR.get_or_init(|| {
        println!("🌐 [MEMORY ORCHESTRATOR] Bangkit. Menyatukan GC, Ownership, dan Manual Malloc!");
        MemoryOrchestrator {
            global_refs: Mutex::new(HashMap::new()),
        }
    })
}

impl MemoryOrchestrator {
    /// Mendaftarkan pointer dari bahasa apapun untuk dilacak secara terpusat!
    pub fn register_pointer(&self, raw_ptr: *mut u8) {
        let ptr_val = raw_ptr as usize;
        let mut refs = self.global_refs.lock().unwrap();
        refs.insert(ptr_val, AtomicUsize::new(1));
        println!("🔗 [ORCHESTRATOR] Pointer {:#x} terdaftar. (RC: 1)", ptr_val);
    }

    /// Bahasa pengutang (contoh V8) menandai dia memakai memori
    pub fn retain_pointer(&self, raw_ptr: *mut u8) {
        let ptr_val = raw_ptr as usize;
        let refs = self.global_refs.lock().unwrap();
        if let Some(rc) = refs.get(&ptr_val) {
            let old = rc.fetch_add(1, Ordering::SeqCst);
            println!("📈 [ORCHESTRATOR] Rc++ pada {:#x} ({} -> {})", ptr_val, old, old + 1);
        }
    }

    /// Bahasa pengutang melepaskan memori (GC V8 mendrop ref, dll)
    /// Mengembalikan true bila memori seharusnya dihapus (RC == 0)
    pub fn release_pointer(&self, raw_ptr: *mut u8) -> bool {
        let ptr_val = raw_ptr as usize;
        let mut refs = self.global_refs.lock().unwrap();
        if let Some(rc) = refs.get(&ptr_val) {
            let old = rc.fetch_sub(1, Ordering::SeqCst);
            println!("📉 [ORCHESTRATOR] Rc-- pada {:#x} ({} -> {})", ptr_val, old, old - 1);
            if old == 1 {
                // Hapai dari global tracking
                refs.remove(&ptr_val);
                println!("☠️ [ORCHESTRATOR] Referensi Habis pada {:#x}! Menginstruksikan C++/Rust Dealloc", ptr_val);
                return true; 
            }
        }
        false
    }
}
