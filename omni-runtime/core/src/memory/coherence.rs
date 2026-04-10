use std::sync::atomic::{fence, Ordering};

pub enum MemoryOrder {
    Acquire,
    Release,
    SeqCst,
}

pub struct HardwareFence;

impl HardwareFence {
    pub fn enforce(order: MemoryOrder) {
        match order {
            MemoryOrder::Acquire => {
                // Mencegah read reordering (MFENCE / DMB)
                fence(Ordering::Acquire);
                println!("[HARDWARE-FENCE] 🧱 ACQUIRE Barrier disuntikkan (Load-Load/Load-Store Dicegah)");
            },
            MemoryOrder::Release => {
                // Mencegah write reordering (MFENCE / DMB)
                fence(Ordering::Release);
                println!("[HARDWARE-FENCE] 🧱 RELEASE Barrier disuntikkan (Load-Store/Store-Store Dicegah)");
            },
            MemoryOrder::SeqCst => {
                // Full Barrier (Lock / MFENCE mutlak)
                fence(Ordering::SeqCst);
                println!("[HARDWARE-FENCE] 🧱 SEQ_CST Mutlak disuntikkan (Konsistensi Global Lintas Core Terkunci)");
            }
        }
    }
}
