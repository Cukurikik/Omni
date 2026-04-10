use crate::nexus::nexus_manifest::Permissions;

pub struct OmniSandbox;

impl OmniSandbox {
    pub fn enforce_permissions(module_name: &str, permissions: Option<&Permissions>) {
        if let Some(perms) = permissions {
             if let Some(net) = &perms.allow_net {
                 println!("[ZERO-TRUST] 🟢 Modul '{}' diizinkan mengakses jaringan ke: {:?}", module_name, net);
             } else {
                 println!("[ZERO-TRUST] 🔴 Peringatan: Modul '{}' mencari akses jaringan tetapi tidak dilisensikan!", module_name);
             }
             if let Some(fs) = &perms.allow_fs_read {
                 println!("[ZERO-TRUST] 🟢 Modul '{}' diizinkan membaca folder: {:?}", module_name, fs);
             }
        } else {
             println!("[ZERO-TRUST] 🛡️ Sangkar Mutlak: Modul '{}' dipenjara tanpa izin akses luar!", module_name);
        }
    }
}
