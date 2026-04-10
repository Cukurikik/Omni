// ==========================================
// 📥 OMNI GET: Package Delivery Mechanism 
// ==========================================
// Mutates Omnifile.toml to add dependencies and
// triggers a subsequent installation resolution via Nexus.
// ==========================================

use std::fs;
use std::path::Path;

pub fn run(package_name: &str) {
    println!("$ omni get {}\n", package_name);

    let omnifile_path = Path::new("Omnifile.toml");
    let fallback_path = Path::new("Omnifile");

    let actual_path = if omnifile_path.exists() {
        omnifile_path
    } else if fallback_path.exists() {
        fallback_path
    } else {
        println!("❌ Omnifile tidak ditemukan di direktori ini.");
        println!("   Jalankan `omni init <nama>` terlebih dahulu.");
        return;
    };

    println!("[NEXUS] 📡 Menghubungi OMNI Registry untuk paket: {}...", package_name);
    
    // Network Delay

    // Simulate standard resolution (latest variant)
    let version_resolved = "latest"; 
    // Secure P2P string simulation
    let mock_hash = format!("sha256:abcd1234efgh5678ijkl9012mnop3456qrst7890uvwx1234yzab5678cdef9012__{}", package_name);

    println!("[NEXUS] ✅ Paket ditemukan! Resolusi versi: {}", version_resolved);

    // Baca dan Mutasi Omnifile
    let mut manifest_content = fs::read_to_string(actual_path)
        .expect("Gagal membaca Omnifile");

    // Sangat sederhana: cari "[dependencies]" , jika ada append, jika tidak, tambahkan sectionnya.
    let target_section = "[dependencies]";
    let dep_line = format!("{} = {{ version = \"{}\", hash = \"{}\" }}", package_name, version_resolved, mock_hash);

    if manifest_content.contains(target_section) || manifest_content.contains("[dependencies.") {
        // Cari posisi akhir dari dependencies block atau sekedar tempel jika [dependencies] murni ada
        if manifest_content.contains(target_section) {
            manifest_content = manifest_content.replace(
                target_section, 
                &format!("{}\n{}", target_section, dep_line)
            );
        } else {
            // Jika ada nested dependencies (seperti [dependencies.intelligence]), kita bisa tambahkan raw deps di akhir
            manifest_content.push_str(&format!("\n[dependencies]\n{}\n", dep_line));
        }
    } else {
        manifest_content.push_str(&format!("\n[dependencies]\n{}\n", dep_line));
    }

    if let Err(e) = fs::write(actual_path, manifest_content) {
        println!("❌ Gagal menulis ke Omnifile: {}", e);
        return;
    }

    println!("[NEXUS] ✏️  Berhasil menambahkan '{}' ke {}", package_name, actual_path.display());
    
    // Menjalankan instalasi segera setelah berhasil menulis Omnifile
    println!("\n[NEXUS] 🚀 Menjalankan re-sinkronisasi dependensi (omni install)...");
    crate::install::run();
}
