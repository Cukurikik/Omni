// ============================================================
// 💾 OMNI Package Cache — ~/.omni/cache
// ============================================================
// Menyimpan paket yang sudah didownload agar tidak perlu
// download ulang. Seperti ~/.npm di Node.js.
// ============================================================

use std::path::{Path, PathBuf};
use std::fs;

/// Lokasi cache OMNI global
pub struct OmniCache {
    cache_dir: PathBuf,
}

impl OmniCache {
    /// Buat cache manager.
    /// Cache disimpan di ~/.omni/cache/ (atau %USERPROFILE%\.omni\cache\ di Windows)
    pub fn new() -> Self {
        let home = std::env::var("USERPROFILE")
            .or_else(|_| std::env::var("HOME"))
            .unwrap_or_else(|_| ".".to_string());
        
        let cache_dir = PathBuf::from(home).join(".omni").join("cache");
        
        // Buat folder cache jika belum ada
        let _ = fs::create_dir_all(&cache_dir);
        
        Self { cache_dir }
    }

    /// Cek apakah paket sudah ada di cache
    pub fn has(&self, name: &str, version: &str) -> bool {
        self.package_path(name, version).exists()
    }

    /// Dapatkan path ke paket di cache
    pub fn package_path(&self, name: &str, version: &str) -> PathBuf {
        self.cache_dir.join(format!("{}@{}", name, version))
    }

    /// Salin paket dari cache ke omni_modules/
    pub fn restore_to(&self, name: &str, version: &str, target: &Path) -> Result<(), String> {
        let cached = self.package_path(name, version);
        
        if !cached.exists() {
            return Err(format!("{}@{} tidak ada di cache", name, version));
        }

        // Copy rekursif dari cache ke target
        copy_dir_all(&cached, target)
            .map_err(|e| format!("Gagal copy dari cache: {}", e))?;

        Ok(())
    }

    /// Simpan paket ke cache dari omni_modules/
    pub fn store_from(&self, name: &str, version: &str, source: &Path) -> Result<(), String> {
        let target = self.package_path(name, version);
        
        if target.exists() {
            // Sudah di-cache, skip
            return Ok(());
        }

        let _ = fs::create_dir_all(&target);
        copy_dir_all(source, &target)
            .map_err(|e| format!("Gagal store ke cache: {}", e))?;

        Ok(())
    }

    /// Hapus seluruh cache (omni cache clean)
    pub fn clean(&self) -> Result<usize, String> {
        if !self.cache_dir.exists() {
            return Ok(0);
        }

        let count = fs::read_dir(&self.cache_dir)
            .map_err(|e| format!("Gagal baca cache dir: {}", e))?
            .count();

        fs::remove_dir_all(&self.cache_dir)
            .map_err(|e| format!("Gagal hapus cache: {}", e))?;
        
        let _ = fs::create_dir_all(&self.cache_dir);
        
        println!("🗑️  Cache dibersihkan: {} paket dihapus", count);
        Ok(count)
    }

    /// Dapatkan ukuran cache (bytes)
    pub fn size(&self) -> u64 {
        dir_size(&self.cache_dir)
    }

    /// Tampilkan info cache
    pub fn info(&self) {
        let size = self.size();
        let count = fs::read_dir(&self.cache_dir)
            .map(|d| d.count())
            .unwrap_or(0);

        let size_mb = size as f64 / 1_048_576.0;

        println!("\n  💾 OMNI CACHE INFO");
        println!("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        println!("  📁 Location : {}", self.cache_dir.display());
        println!("  📦 Packages : {}", count);
        println!("  💿 Size     : {:.2} MB", size_mb);
        println!();
    }
}

/// Salin folder secara rekursif
fn copy_dir_all(src: &Path, dst: &Path) -> std::io::Result<()> {
    fs::create_dir_all(dst)?;
    
    for entry in fs::read_dir(src)? {
        let entry = entry?;
        let ty = entry.file_type()?;
        let target = dst.join(entry.file_name());
        
        if ty.is_dir() {
            copy_dir_all(&entry.path(), &target)?;
        } else {
            fs::copy(entry.path(), target)?;
        }
    }
    
    Ok(())
}

/// Hitung ukuran folder secara rekursif
fn dir_size(path: &Path) -> u64 {
    if !path.exists() {
        return 0;
    }
    
    let mut total: u64 = 0;
    
    if let Ok(entries) = fs::read_dir(path) {
        for entry in entries.flatten() {
            let ty = entry.file_type().unwrap_or_else(|_| unreachable!());
            if ty.is_file() {
                total += entry.metadata().map(|m| m.len()).unwrap_or(0);
            } else if ty.is_dir() {
                total += dir_size(&entry.path());
            }
        }
    }
    
    total
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cache_path() {
        let cache = OmniCache::new();
        let path = cache.package_path("omni-std", "1.0.0");
        assert!(path.to_string_lossy().contains("omni-std@1.0.0"));
    }
}
