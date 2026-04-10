use std::fs;
use std::path::Path;

// ONE TRUE STYLE FORMATTER
pub fn run() {
    println!("$ omni fmt");
    
    let mut files_formatted = 0;
    
    // Sederhana: kita cari semua file .omni di direktori aktif
    let paths = fs::read_dir("./").unwrap();
    
    for path in paths {
        let path = path.unwrap().path();
        if path.extension().and_then(|s| s.to_str()) == Some("omni") {
            if format_file(&path) {
                files_formatted += 1;
            }
        }
    }
    
    println!("> {} file disesuaikan dengan Standar OMNI. (One True Style)", files_formatted);
}

fn format_file(path: &Path) -> bool {
    let content = match fs::read_to_string(path) {
        Ok(c) => c,
        Err(_) => return false,
    };
    
    let formatted = format_source(&content);
    
    if content != formatted {
        let _ = fs::write(path, formatted);
        println!("  ✏️  Formatted: {}", path.display());
        true
    } else {
        println!("  ✅ Unchanged: {}", path.display());
        false
    }
}

// Deterministic Formatting Engine
fn format_source(source: &str) -> String {
    let mut formatted = String::new();
    let mut indent_level: usize = 0;
    let mut in_string = false;
    
    let lines: Vec<&str> = source.lines().collect();
    
    for line in lines {
        let trimmed = line.trim();
        if trimmed.is_empty() {
            formatted.push('\n');
            continue;
        }
        
        // Cek apakah baris ini mengurangi indentasi sebelum ngeprint
        if trimmed.starts_with('}') {
            indent_level = indent_level.saturating_sub(1);
        }
        
        let indentation = "    ".repeat(indent_level);
        formatted.push_str(&indentation);
        
        let mut char_iter = trimmed.chars().peekable();
        let mut last_char = ' ';
        
        while let Some(c) = char_iter.next() {
            if c == '"' {
                in_string = !in_string;
            }
            
            if !in_string {
                if c == '{' {
                    // One True Brace style: pasang spasi sebelum '{' kecuali di awal
                    if last_char != ' ' && last_char != '{' {
                        // Jika belum ada spasi, hapus trailing char yg terakhir lalu tambahkan space + '{'
                        // Untuk simplicity karena kita push per char:
                    }
                    indent_level += 1;
                } else if c == '}' {
                    // Sudah dikurangi di awal baris jika startswith '}'. 
                    // Jika di tengah baris, kurangi juga.
                    if indent_level > 0 && !trimmed.starts_with('}') {
                        indent_level -= 1;
                    }
                }
            }
            formatted.push(c);
            last_char = c;
        }
        formatted.push('\n');
    }
    
    formatted.trim_end().to_string() + "\n"
}
