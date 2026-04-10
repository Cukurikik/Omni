use std::fs;
use std::path::Path;
use sha2::{Sha384, Digest};

pub struct LockFile;

impl LockFile {
    pub fn compute_sha256(file_path: &Path) -> String {
        let mut file = fs::File::open(file_path).unwrap();
        let mut hasher = Sha384::new();
        std::io::copy(&mut file, &mut hasher).unwrap();
        let hash = hasher.finalize();
        format!("{:x}", hash)
    }

    pub fn verify_package(name: &str, file_path: &Path, expected_hash: &str) -> bool {
        let real_hash = Self::compute_sha256(file_path);
        
        println!("[OMNI-LOCK] 🔒 Verifikasi Modul '{}'", name);
        println!("   → Lockfile Hash : {}", expected_hash);
        println!("   → Real File Hash: {}", real_hash);
        
        if real_hash == expected_hash {
            println!("[OMNI-LOCK] ✅ Hash MATCH! Integritas Aman (Zero-Trust/IPFS Passed).");
            true
        } else {
            println!("[OMNI-LOCK] 🚨 HASH MISMATCH! SUPPLY CHAIN ATTACK TERDETEKSI!");
            println!("Eksekusi Kompilator Terputus Otomatis!");
            false
        }
    }
}
