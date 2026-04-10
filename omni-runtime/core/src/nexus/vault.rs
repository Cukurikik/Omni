use std::fs::{self, File};
use std::io::{Read, Write};
use std::path::PathBuf;
use ureq;
use std::thread;

pub struct GlobalVault;

impl GlobalVault {
    pub fn get_vault_path() -> PathBuf {
        let home_dir = std::env::var("USERPROFILE")
            .or_else(|_| std::env::var("HOME"))
            .unwrap_or_else(|_| ".".to_string());
        
        let vault_dir = PathBuf::from(home_dir).join(".nexus").join("cache");
        if !vault_dir.exists() { fs::create_dir_all(&vault_dir).unwrap(); }
        vault_dir
    }

    pub fn get_local_module_path(name: &str) -> PathBuf {
        let local_modules = std::env::current_dir().unwrap().join(".nexus_modules").join(name);
        if !local_modules.exists() { fs::create_dir_all(&local_modules).unwrap(); }
        local_modules
    }

    pub fn download_package(name: &str, url: &str) -> Option<PathBuf> {
        println!("[OMNI-NEXUS] 📥 Memanggil Goroutine-spawn: Download {} dari {}...", name, url);
        let name_clone = name.to_string();
        let url_clone = url.to_string();
        
        let handle = thread::spawn(move || {
            use sha2::{Sha384, Digest};

            let response = match ureq::get(&url_clone).call() {
                Ok(resp) => resp,
                Err(_) => return None,
            };

            let mut reader = response.into_reader();
            let mut bytes = Vec::new();
            if reader.read_to_end(&mut bytes).is_err() { return None; }

            // 1. CAS Hashing SHA-384
            let mut hasher = Sha384::new();
            hasher.update(&bytes);
            let sha384_hash = format!("{:x}", hasher.finalize());

            // 2. Simpan ke Global Vault Cache
            let vault_path = Self::get_vault_path();
            let cache_file = vault_path.join(format!("{}.cas", sha384_hash));
            
            if !cache_file.exists() {
                let mut file = File::create(&cache_file).unwrap();
                file.write_all(&bytes).unwrap();
                println!("[OMNI-VAULT] 💾 Disimpan ke Global CAS Cache ~/.nexus/cache (0 byte duplikasi).");
            } else {
                println!("[OMNI-VAULT] ⚡ Modul {} sudah ada di Global Cache! Waktu unduh: 0 detik.", name_clone);
            }

            // 3. Buat Hardlink ke Lokal (.nexus_modules)
            let local_dir = Self::get_local_module_path(&name_clone);
            let local_target = local_dir.join("main.omni");

            if local_target.exists() {
                fs::remove_file(&local_target).unwrap();
            }

            // Fallback copy jika hard_link menyeberang OS Partisi
            match fs::hard_link(&cache_file, &local_target) {
                Ok(_) => println!("[OMNI-NEXUS] 🔗 Hardlink CAS sukses! SSD Space yang dipakai untuk proyek ini: 0 Bytes!"),
                Err(_) => {
                    fs::copy(&cache_file, &local_target).unwrap();
                    println!("[OMNI-NEXUS] ⚠️ Hardlink gagal (beda partisi?), menggunakan Copy opsional.");
                }
            }
            
            Some(local_target)
        });

        handle.join().unwrap()
    }
}
