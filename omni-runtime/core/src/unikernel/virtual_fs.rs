#![allow(dead_code)]
// ==========================================
// 💾 OMNI VIRTUAL FILESYSTEM (In-RAM VFS)
// ==========================================
// Unikernel tidak punya hard drive.
// Semua file operations terjadi di RAM.
//
// FITUR:
//   - Create / Read / Write / Delete files
//   - Directory tree structure
//   - Mount point abstraction
//   - Serializable (can be embedded into unikernel image)
//
// CONTOH PENGGUNAAN DARI OMNI:
//   System.mount_virtual_fs();
//   let file = fs.open("/config/server.toml");
// ==========================================

use std::collections::HashMap;

/// Tipe entry dalam filesystem
#[derive(Debug, Clone)]
pub enum FSEntry {
    File {
        content: Vec<u8>,
        created_at: u64,
        modified_at: u64,
        permissions: u16,  // Unix-style: 0o755
    },
    Directory {
        children: HashMap<String, FSEntry>,
        created_at: u64,
    },
}

/// 💾 THE OMNI VIRTUAL FILESYSTEM
pub struct VirtualFS {
    root: FSEntry,
    total_bytes: usize,
    total_files: usize,
    total_dirs: usize,
}

impl VirtualFS {
    pub fn new() -> Self {
        Self {
            root: FSEntry::Directory {
                children: HashMap::new(),
                created_at: 0,
            },
            total_bytes: 0,
            total_files: 0,
            total_dirs: 1, // Root directory
        }
    }

    /// Create a directory (and all parent directories)
    pub fn mkdir(&mut self, path: &str) {
        let parts: Vec<&str> = path.trim_matches('/').split('/').filter(|p| !p.is_empty()).collect();
        let mut current = &mut self.root;

        for part in parts {
            match current {
                FSEntry::Directory { children, .. } => {
                    if !children.contains_key(part) {
                        children.insert(part.to_string(), FSEntry::Directory {
                            children: HashMap::new(),
                            created_at: 0,
                        });
                        self.total_dirs += 1;
                    }
                    current = children.get_mut(part).unwrap();
                },
                _ => return, // Can't create dir inside a file
            }
        }
    }

    /// Write a file (creates parent directories if needed)
    pub fn write_file(&mut self, path: &str, content: &[u8]) {
        let parts: Vec<&str> = path.trim_matches('/').split('/').filter(|p| !p.is_empty()).collect();
        
        if parts.is_empty() {
            return;
        }

        // Create parent directories
        if parts.len() > 1 {
            let parent_path = parts[..parts.len() - 1].join("/");
            self.mkdir(&parent_path);
        }

        // Navigate to parent
        let mut current = &mut self.root;
        for part in &parts[..parts.len() - 1] {
            match current {
                FSEntry::Directory { children, .. } => {
                    current = children.get_mut(*part).unwrap();
                },
                _ => return,
            }
        }

        // Create the file
        let filename = parts.last().unwrap();
        let file_size = content.len();
        
        match current {
            FSEntry::Directory { children, .. } => {
                // Check if updating existing file
                if children.contains_key(*filename) {
                    if let Some(FSEntry::File { content: old_content, .. }) = children.get(*filename) {
                        self.total_bytes -= old_content.len();
                    } else {
                        self.total_files += 1;
                    }
                } else {
                    self.total_files += 1;
                }

                children.insert(filename.to_string(), FSEntry::File {
                    content: content.to_vec(),
                    created_at: 0,
                    modified_at: 0,
                    permissions: 0o644,
                });
                self.total_bytes += file_size;
            },
            _ => {},
        }
    }

    /// Read a file's content
    pub fn read_file(&self, path: &str) -> Option<&[u8]> {
        let parts: Vec<&str> = path.trim_matches('/').split('/').filter(|p| !p.is_empty()).collect();
        let mut current = &self.root;

        for (i, part) in parts.iter().enumerate() {
            match current {
                FSEntry::Directory { children, .. } => {
                    match children.get(*part) {
                        Some(entry) => {
                            if i == parts.len() - 1 {
                                // Last part — should be a file
                                if let FSEntry::File { content, .. } = entry {
                                    return Some(content);
                                }
                            }
                            current = entry;
                        },
                        None => return None,
                    }
                },
                _ => return None,
            }
        }
        None
    }

    /// Delete a file
    pub fn delete(&mut self, path: &str) -> bool {
        let parts: Vec<&str> = path.trim_matches('/').split('/').filter(|p| !p.is_empty()).collect();
        
        if parts.is_empty() {
            return false;
        }

        // Navigate to parent
        let mut current = &mut self.root;
        for part in &parts[..parts.len() - 1] {
            match current {
                FSEntry::Directory { children, .. } => {
                    if let Some(entry) = children.get_mut(*part) {
                        current = entry;
                    } else {
                        return false;
                    }
                },
                _ => return false,
            }
        }

        let filename = parts.last().unwrap();
        match current {
            FSEntry::Directory { children, .. } => {
                if let Some(entry) = children.remove(*filename) {
                    match entry {
                        FSEntry::File { content, .. } => {
                            self.total_bytes -= content.len();
                            self.total_files -= 1;
                        },
                        FSEntry::Directory { .. } => {
                            self.total_dirs -= 1;
                        },
                    }
                    true
                } else {
                    false
                }
            },
            _ => false,
        }
    }

    /// Check if a path exists
    pub fn exists(&self, path: &str) -> bool {
        let parts: Vec<&str> = path.trim_matches('/').split('/').filter(|p| !p.is_empty()).collect();
        let mut current = &self.root;

        for part in &parts {
            match current {
                FSEntry::Directory { children, .. } => {
                    match children.get(*part) {
                        Some(entry) => current = entry,
                        None => return false,
                    }
                },
                _ => return false,
            }
        }
        true
    }

    /// List files in a directory
    pub fn list_dir(&self, path: &str) -> Vec<String> {
        let parts: Vec<&str> = path.trim_matches('/').split('/').filter(|p| !p.is_empty()).collect();
        let mut current = &self.root;

        for part in &parts {
            match current {
                FSEntry::Directory { children, .. } => {
                    match children.get(*part) {
                        Some(entry) => current = entry,
                        None => return Vec::new(),
                    }
                },
                _ => return Vec::new(),
            }
        }

        match current {
            FSEntry::Directory { children, .. } => {
                let mut entries: Vec<String> = children.keys().cloned().collect();
                entries.sort();
                entries
            },
            _ => Vec::new(),
        }
    }

    /// Get total number of files
    pub fn file_count(&self) -> usize {
        self.total_files
    }

    /// Get total number of directories
    pub fn dir_count(&self) -> usize {
        self.total_dirs
    }

    /// Get total bytes used
    pub fn total_bytes_used(&self) -> usize {
        self.total_bytes
    }

    /// Serialize the entire VFS to bytes (for embedding in unikernel image)
    pub fn serialize(&self) -> Vec<u8> {
        let mut output = Vec::new();
        
        // Header: OMNI-VFS + version
        output.extend_from_slice(b"OMNI-VFS-v1\x00");
        output.extend_from_slice(&(self.total_files as u32).to_le_bytes());
        output.extend_from_slice(&(self.total_dirs as u32).to_le_bytes());
        output.extend_from_slice(&(self.total_bytes as u64).to_le_bytes());
        
        // Serialize the tree recursively  
        self.serialize_entry(&self.root, "/", &mut output);
        
        output
    }

    fn serialize_entry(&self, entry: &FSEntry, path: &str, output: &mut Vec<u8>) {
        match entry {
            FSEntry::File { content, permissions, .. } => {
                output.push(b'F'); // File marker
                let path_bytes = path.as_bytes();
                output.extend_from_slice(&(path_bytes.len() as u16).to_le_bytes());
                output.extend_from_slice(path_bytes);
                output.extend_from_slice(&(*permissions).to_le_bytes());
                output.extend_from_slice(&(content.len() as u32).to_le_bytes());
                output.extend_from_slice(content);
            },
            FSEntry::Directory { children, .. } => {
                output.push(b'D'); // Directory marker
                let path_bytes = path.as_bytes();
                output.extend_from_slice(&(path_bytes.len() as u16).to_le_bytes());
                output.extend_from_slice(path_bytes);
                output.extend_from_slice(&(children.len() as u16).to_le_bytes());
                
                for (name, child) in children {
                    let child_path = if path == "/" {
                        format!("/{}", name)
                    } else {
                        format!("{}/{}", path, name)
                    };
                    self.serialize_entry(child, &child_path, output);
                }
            },
        }
    }

    /// Print the filesystem tree
    pub fn print_tree(&self) {
        println!("💾 OMNI Virtual Filesystem:");
        println!("═══════════════════════════════════");
        self.print_entry(&self.root, "/", 0);
        println!("═══════════════════════════════════");
        println!("Files: {} | Dirs: {} | Total: {} bytes", 
            self.total_files, self.total_dirs, self.total_bytes);
    }

    fn print_entry(&self, entry: &FSEntry, name: &str, depth: usize) {
        let indent = "  ".repeat(depth);
        match entry {
            FSEntry::File { content, .. } => {
                println!("{}📄 {} ({} bytes)", indent, name, content.len());
            },
            FSEntry::Directory { children, .. } => {
                println!("{}📁 {}/", indent, name);
                let mut sorted_children: Vec<_> = children.iter().collect();
                sorted_children.sort_by_key(|(k, _)| k.to_string());
                for (child_name, child) in sorted_children {
                    self.print_entry(child, child_name, depth + 1);
                }
            },
        }
    }
}
