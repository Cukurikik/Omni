// ==========================================
// 🦠 NODE PARASITE DAEMON — EKSEKUSI NYATA
// ==========================================
// BUKAN SIMULASI. Subprocess Node.js asli.
// Digunakan untuk heavy I/O workloads yang
// membutuhkan event loop penuh (networking, fs).
// V8 Isolate murni TIDAK punya event loop.
// ==========================================

use anyhow::Result;
use std::process::{Command, Stdio};
use std::io::Read;

pub struct NodeParasiteDaemon {
    active: bool,
    node_version: String,
}

impl NodeParasiteDaemon {
    pub fn new() -> Self {
        Self { 
            active: false,
            node_version: String::new(),
        }
    }

    /// Deteksi dan kunci Node.js di sistem
    pub fn spawn_daemon(&mut self) -> Result<()> {
        println!("🦠 [OMNI-PARASITE] Mendeteksi Node.js untuk heavy workloads...");
        
        let output = Command::new("node")
            .arg("--version")
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .output();

        match output {
            Ok(o) => {
                let ver = String::from_utf8_lossy(&o.stdout).trim().to_string();
                if ver.starts_with('v') {
                    println!("  🦇 Node.js {} siap untuk heavy workloads", ver);
                    self.node_version = ver;
                    self.active = true;
                } else {
                    println!("  ⚠️ Node.js tidak dikenali — parasite nonaktif");
                    self.active = false;
                }
            }
            Err(_) => {
                println!("  ⚠️ Node.js tidak ditemukan — parasite nonaktif (V8 Isolate tetap aktif)");
                self.active = false;
            }
        }
        
        Ok(())
    }

    /// Eksekusi NYATA melalui Node.js subprocess
    /// Untuk workloads yang butuh event loop (async, networking, etc)
    pub fn execute_heavy_workload(&self, js_payload: &str) -> Result<()> {
        if !self.active {
            println!("  ⏭️ [PARASITE] Dilewati — Node.js tidak tersedia");
            return Ok(());
        }

        println!("⚡ [OMNI-PARASITE] Mengeksekusi heavy workload di Node.js...");

        // Bungkus dengan OMNI runtime polyfills
        let wrapped = format!(r#"
'use strict';
function print() {{
    var args = Array.prototype.slice.call(arguments);
    var line = args.map(function(a) {{
        if (typeof a === 'object' && a !== null) return JSON.stringify(a);
        return String(a);
    }}).join(' ');
    process.stdout.write(line + '\n');
}}

var OmniMath = {{
    tensorOp: function(op, a, b) {{
        switch(op) {{
            case '.*': return a * b;
            case '.+': return a + b;
            case '.-': return a - b;
            case './': return a / b;
            default: return 0;
        }}
    }}
}};

var OmniGraph = {{
    query: function(q) {{ return '[GraphQL Result: ' + q.trim() + ']'; }}
}};

var OmniUI = {{
    createElement: function(tag, props, children) {{
        return {{ tag: tag, props: props, children: children }};
    }}
}};

try {{
{code}
}} catch(err) {{
    process.stderr.write('OMNI Runtime Error: ' + err.message + '\n');
    if (err.stack) process.stderr.write(err.stack + '\n');
    process.exit(1);
}}
"#, code = js_payload);

        let mut child = Command::new("node")
            .arg("-e")
            .arg(&wrapped)
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .map_err(|e| anyhow::anyhow!("Gagal menjalankan Node.js: {}", e))?;

        let mut stdout = String::new();
        let mut stderr = String::new();

        if let Some(mut out) = child.stdout.take() {
            out.read_to_string(&mut stdout)?;
        }
        if let Some(mut err) = child.stderr.take() {
            err.read_to_string(&mut stderr)?;
        }

        let status = child.wait()?;

        // Tampilkan output nyata
        if !stdout.is_empty() {
            println!("\n┌─── NODE OUTPUT ────────────────────────┐");
            for line in stdout.lines() {
                println!("│  {}", line);
            }
            println!("└────────────────────────────────────────┘");
        }

        if !stderr.is_empty() {
            println!("\n┌─── NODE ERRORS ────────────────────────┐");
            for line in stderr.lines() {
                println!("│  ⚠️  {}", line);
            }
            println!("└────────────────────────────────────────┘");
        }

        if status.success() {
            println!("✅ [PARASITE] Eksekusi berhasil (exit: 0)");
        } else {
            println!("❌ [PARASITE] Eksekusi gagal (exit: {})", status.code().unwrap_or(-1));
        }

        Ok(())
    }
}
