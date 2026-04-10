// ============================================================
// 🦀 OMNI-FS-CORE: Rust Native File System Operations
// ============================================================
// Pengganti total Node.js `fs` module dengan zero-cost abstraction.
// Setiap operasi menggunakan monadic Result<T, FsError> — 
// TIDAK ADA try/catch konvensional yang diizinkan.
// ============================================================

use std::fs;
use std::io::{self, Read, Write, BufReader, BufWriter};
use std::path::{Path, PathBuf};
use std::time::SystemTime;

/// Error domain khusus untuk seluruh operasi File System OMNI
#[derive(Debug)]
pub enum FsError {
    NotFound(String),
    PermissionDenied(String),
    AlreadyExists(String),
    IoError(io::Error),
    InvalidPath(String),
}

impl From<io::Error> for FsError {
    fn from(e: io::Error) -> Self {
        match e.kind() {
            io::ErrorKind::NotFound => FsError::NotFound(e.to_string()),
            io::ErrorKind::PermissionDenied => FsError::PermissionDenied(e.to_string()),
            io::ErrorKind::AlreadyExists => FsError::AlreadyExists(e.to_string()),
            _ => FsError::IoError(e),
        }
    }
}

/// Metadata file hasil dari stat_file
#[derive(Debug)]
pub struct OmniFileMeta {
    pub path: PathBuf,
    pub size_bytes: u64,
    pub is_dir: bool,
    pub is_symlink: bool,
    pub modified: Option<SystemTime>,
    pub created: Option<SystemTime>,
    pub readonly: bool,
}

/// Entri hasil dari list_dir
#[derive(Debug)]
pub struct OmniDirEntry {
    pub name: String,
    pub path: PathBuf,
    pub is_dir: bool,
    pub size_bytes: u64,
}

// ============================================================
// Operasi File Inti (Pengganti fs.readFileSync, fs.writeFileSync, dll)
// ============================================================

/// Membaca seluruh isi file sebagai byte vector (zero-copy ready).
/// Ekuivalen Node.js: `fs.readFileSync(path)`
pub fn read_file(path: &Path) -> Result<Vec<u8>, FsError> {
    let file = fs::File::open(path)?;
    let mut reader = BufReader::new(file);
    let mut buffer = Vec::new();
    reader.read_to_end(&mut buffer)?;
    Ok(buffer)
}

/// Membaca file sebagai UTF-8 string.
/// Ekuivalen Node.js: `fs.readFileSync(path, 'utf-8')`
pub fn read_file_string(path: &Path) -> Result<String, FsError> {
    let bytes = read_file(path)?;
    String::from_utf8(bytes).map_err(|e| FsError::InvalidPath(
        format!("File bukan UTF-8 valid: {}", e)
    ))
}

/// Menulis data bytes ke file, menimpa jika sudah ada.
/// Ekuivalen Node.js: `fs.writeFileSync(path, data)`
pub fn write_file(path: &Path, data: &[u8]) -> Result<(), FsError> {
    let file = fs::File::create(path)?;
    let mut writer = BufWriter::new(file);
    writer.write_all(data)?;
    writer.flush()?;
    Ok(())
}

/// Menambahkan data ke akhir file (append mode).
/// Ekuivalen Node.js: `fs.appendFileSync(path, data)`
pub fn append_file(path: &Path, data: &[u8]) -> Result<(), FsError> {
    let file = fs::OpenOptions::new()
        .append(true)
        .create(true)
        .open(path)?;
    let mut writer = BufWriter::new(file);
    writer.write_all(data)?;
    writer.flush()?;
    Ok(())
}

/// Menghapus file dari sistem.
/// Ekuivalen Node.js: `fs.unlinkSync(path)`
pub fn remove_file(path: &Path) -> Result<(), FsError> {
    fs::remove_file(path)?;
    Ok(())
}

/// Menyalin file dari sumber ke tujuan.
/// Ekuivalen Node.js: `fs.copyFileSync(src, dest)`
pub fn copy_file(src: &Path, dest: &Path) -> Result<u64, FsError> {
    let bytes_copied = fs::copy(src, dest)?;
    Ok(bytes_copied)
}

/// Memindahkan/mengganti nama file.
/// Ekuivalen Node.js: `fs.renameSync(old, new)`
pub fn rename_file(from: &Path, to: &Path) -> Result<(), FsError> {
    fs::rename(from, to)?;
    Ok(())
}

// ============================================================
// Operasi Direktori
// ============================================================

/// Membuat direktori baru (non-rekursif).
/// Ekuivalen Node.js: `fs.mkdirSync(path)`
pub fn create_dir(path: &Path) -> Result<(), FsError> {
    fs::create_dir(path)?;
    Ok(())
}

/// Membuat direktori secara rekursif (termasuk parent).
/// Ekuivalen Node.js: `fs.mkdirSync(path, { recursive: true })`
pub fn create_dir_recursive(path: &Path) -> Result<(), FsError> {
    fs::create_dir_all(path)?;
    Ok(())
}

/// Menghapus direktori secara rekursif.
/// Ekuivalen Node.js: `fs.rmSync(path, { recursive: true, force: true })`
pub fn remove_dir_recursive(path: &Path) -> Result<(), FsError> {
    fs::remove_dir_all(path)?;
    Ok(())
}

/// Mendaftar isi direktori sebagai vektor OmniDirEntry.
/// Ekuivalen Node.js: `fs.readdirSync(path, { withFileTypes: true })`
pub fn list_dir(path: &Path) -> Result<Vec<OmniDirEntry>, FsError> {
    let mut entries = Vec::new();
    for entry in fs::read_dir(path)? {
        let entry = entry?;
        let metadata = entry.metadata()?;
        entries.push(OmniDirEntry {
            name: entry.file_name().to_string_lossy().into_owned(),
            path: entry.path(),
            is_dir: metadata.is_dir(),
            size_bytes: metadata.len(),
        });
    }
    Ok(entries)
}

// ============================================================
// Operasi Metadata & Stat
// ============================================================

/// Mengambil metadata lengkap dari file atau direktori.
/// Ekuivalen Node.js: `fs.statSync(path)`
pub fn stat_file(path: &Path) -> Result<OmniFileMeta, FsError> {
    let metadata = fs::metadata(path)?;
    Ok(OmniFileMeta {
        path: path.to_path_buf(),
        size_bytes: metadata.len(),
        is_dir: metadata.is_dir(),
        is_symlink: metadata.file_type().is_symlink(),
        modified: metadata.modified().ok(),
        created: metadata.created().ok(),
        readonly: metadata.permissions().readonly(),
    })
}

/// Memeriksa apakah path ada di filesystem.
/// Ekuivalen Node.js: `fs.existsSync(path)`
pub fn exists(path: &Path) -> bool {
    path.exists()
}

/// Memeriksa apakah path adalah file.
pub fn is_file(path: &Path) -> bool {
    path.is_file()
}

/// Memeriksa apakah path adalah direktori.
pub fn is_dir(path: &Path) -> bool {
    path.is_dir()
}

// ============================================================
// Unit Tests
// ============================================================

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::Path;

    #[test]
    fn test_write_and_read_file() {
        let test_path = Path::new("/tmp/omni_test_rw.txt");
        let data = b"OMNI Framework Test Data";
        
        write_file(test_path, data).expect("Write harus sukses");
        let result = read_file(test_path).expect("Read harus sukses");
        
        assert_eq!(result, data);
        remove_file(test_path).expect("Cleanup harus sukses");
    }

    #[test]
    fn test_stat_file() {
        let test_path = Path::new("/tmp/omni_test_stat.txt");
        write_file(test_path, b"stat_test").expect("Write harus sukses");
        
        let meta = stat_file(test_path).expect("Stat harus sukses");
        assert!(!meta.is_dir);
        assert_eq!(meta.size_bytes, 9);
        
        remove_file(test_path).expect("Cleanup harus sukses");
    }

    #[test]
    fn test_create_and_list_dir() {
        let dir_path = Path::new("/tmp/omni_test_dir");
        if exists(dir_path) {
            remove_dir_recursive(dir_path).ok();
        }
        
        create_dir(dir_path).expect("Mkdir harus sukses");
        write_file(&dir_path.join("a.txt"), b"a").ok();
        write_file(&dir_path.join("b.txt"), b"b").ok();
        
        let entries = list_dir(dir_path).expect("Readdir harus sukses");
        assert_eq!(entries.len(), 2);
        
        remove_dir_recursive(dir_path).expect("Cleanup harus sukses");
    }
}
