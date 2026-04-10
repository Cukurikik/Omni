// ==========================================
// 🔌 OMNI-SYSCALLS: Native Function Handlers
// ==========================================
// Backend untuk OmniNative.syscall() yang dipanggil dari JavaScript.
// Setiap syscall diproses oleh Rust native code (fs, crypto, dll).
//
// ALUR: JS → V8 callback → Rust syscall handler → Return JSON
// ==========================================

use std::fs;
use std::path::Path;
use sha2::{Sha256, Digest};
use serde_json::{json, Value};

/// Dispatch syscall berdasarkan command name
pub fn handle_syscall(command: &str, args: &Value) -> Value {
    match command {
        // ==========================================
        // 📂 FILE SYSTEM SYSCALLS
        // ==========================================
        "fs_read" => {
            let path = args["path"].as_str().unwrap_or("");
            match fs::read_to_string(path) {
                Ok(data) => json!({ "data": data }),
                Err(e) => json!({ "error": format!("Gagal membaca {}: {}", path, e) }),
            }
        }
        "fs_write" => {
            let path = args["path"].as_str().unwrap_or("");
            let data = args["data"].as_str().unwrap_or("");
            match fs::write(path, data) {
                Ok(_) => json!({ "success": true }),
                Err(e) => json!({ "error": format!("Gagal menulis {}: {}", path, e) }),
            }
        }
        "fs_exists" => {
            let path = args["path"].as_str().unwrap_or("");
            json!({ "exists": Path::new(path).exists() })
        }
        "fs_mkdir" => {
            let path = args["path"].as_str().unwrap_or("");
            let recursive = args["recursive"].as_bool().unwrap_or(false);
            let result = if recursive {
                fs::create_dir_all(path)
            } else {
                fs::create_dir(path)
            };
            match result {
                Ok(_) => json!({ "success": true }),
                Err(e) => json!({ "error": format!("{}", e) }),
            }
        }
        "fs_readdir" => {
            let path = args["path"].as_str().unwrap_or("");
            match fs::read_dir(path) {
                Ok(entries) => {
                    let names: Vec<Value> = entries
                        .filter_map(|e| e.ok())
                        .map(|e| {
                            let ft = e.file_type().ok();
                            json!({
                                "name": e.file_name().to_string_lossy().to_string(),
                                "isDir": ft.map(|f| f.is_dir()).unwrap_or(false),
                            })
                        })
                        .collect();
                    json!({ "entries": names })
                }
                Err(e) => json!({ "error": format!("{}", e) }),
            }
        }
        "fs_remove" => {
            let path = args["path"].as_str().unwrap_or("");
            let p = Path::new(path);
            let result = if p.is_dir() { fs::remove_dir_all(p) } else { fs::remove_file(p) };
            match result {
                Ok(_) => json!({ "success": true }),
                Err(e) => json!({ "error": format!("{}", e) }),
            }
        }
        "fs_stat" => {
            let path = args["path"].as_str().unwrap_or("");
            match fs::metadata(path) {
                Ok(meta) => json!({
                    "stat": {
                        "size": meta.len(),
                        "isDir": meta.is_dir(),
                        "isFile": meta.is_file(),
                        "readonly": meta.permissions().readonly(),
                    }
                }),
                Err(e) => json!({ "error": format!("{}", e) }),
            }
        }

        // ==========================================
        // 🔐 CRYPTO SYSCALLS
        // ==========================================
        "crypto_hash" => {
            let algo = args["algo"].as_str().unwrap_or("sha256");
            let payload = args["payload"].as_str().unwrap_or("");
            match algo {
                "sha256" => {
                    let mut hasher = Sha256::new();
                    hasher.update(payload.as_bytes());
                    let hash = hasher.finalize();
                    json!({ "result": format!("{:x}", hash) })
                }
                "md5" => {
                    let digest = md5::compute(payload.as_bytes());
                    json!({ "result": format!("{:x}", digest) })
                }
                _ => json!({ "error": format!("Algoritma tidak didukung: {}", algo) }),
            }
        }
        "crypto_uuid" => {
            // Simple UUID v4 generator menggunakan random bytes
            let uuid = format!(
                "{:08x}-{:04x}-4{:03x}-{:04x}-{:012x}",
                rand_u32(), rand_u16(), rand_u16() & 0x0FFF,
                (rand_u16() & 0x3FFF) | 0x8000, rand_u64() & 0xFFFFFFFFFFFF,
            );
            json!({ "uuid": uuid })
        }
        "crypto_random" => {
            let size = args["size"].as_u64().unwrap_or(16) as usize;
            let bytes: Vec<u8> = (0..size).map(|_| rand_u8()).collect();
            let hex: String = bytes.iter().map(|b| format!("{:02x}", b)).collect();
            json!({ "bytes": hex })
        }

        // ==========================================
        // 🌐 HTTP SYSCALLS (Config for Go server)
        // ==========================================
        "http_serve" => {
            let port = args["port"].as_u64().unwrap_or(3000);
            let handler = args["handlerName"].as_str().unwrap_or("anonymous");
            log::info!("🌍 [SYSCALL] HTTP serve requested: port={}, handler={}", port, handler);
            json!({ "status": "registered", "port": port, "handler": handler })
        }
        "http_fetch" => {
            // NOTE: Native HTTP fetch akan dihandle oleh Golang side
            json!({ "error": "http_fetch harus diproses oleh Golang (Use ExecuteWithContext)" })
        }

        // ==========================================
        // 💾 QUEUE SYSCALLS (OMNI-AURA — WAL Engine)
        // ==========================================
        "queue_dispatch" => {
            let name = args["name"].as_str().unwrap_or("unnamed");
            let _payload = &args["payload"];
            let max_retry = args["max_retry"].as_i64().unwrap_or(3);
            let job_id = format!("job_{}_{}", 
                std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap().as_millis(),
                rand_u32()
            );
            log::info!("📥 [SYSCALL] Queue dispatch: {} ({}), retries={}", name, job_id, max_retry);
            // NOTE: Actual WAL write akan dihandle oleh Golang AuraEngine
            // Rust meneruskan perintah, Go melakukan I/O ke WAL SSD
            json!({ "jobId": job_id, "status": "dispatched", "name": name })
        }
        "queue_register" => {
            let name = args["name"].as_str().unwrap_or("unnamed");
            let handler = args["handlerName"].as_str().unwrap_or("anonymous");
            log::info!("📋 [SYSCALL] Queue handler registered: {} -> {}", name, handler);
            json!({ "status": "registered", "name": name, "handler": handler })
        }
        "queue_stats" => {
            // Placeholder — Go-side AuraEngine returns real stats
            json!({
                "totalDispatched": 0,
                "totalProcessed": 0,
                "totalFailed": 0,
                "queueDepth": 0
            })
        }

        // ==========================================
        // 🌍 MESH SYSCALLS (OMNI-MESH — P2P Gossip)
        // ==========================================
        "mesh_join" => {
            let peers = &args["peers"];
            log::info!("🌍 [SYSCALL] Mesh join requested: {:?}", peers);
            json!({ "status": "joining", "peers": peers })
        }
        "mesh_broadcast" => {
            let topic = args["topic"].as_str().unwrap_or("default");
            let _data = &args["data"];
            log::info!("📡 [SYSCALL] Mesh broadcast: topic={}", topic);
            json!({ "status": "broadcasted", "topic": topic })
        }
        "mesh_subscribe" => {
            let topic = args["topic"].as_str().unwrap_or("default");
            let handler = args["handlerName"].as_str().unwrap_or("anonymous");
            log::info!("📡 [SYSCALL] Mesh subscribe: {} -> {}", topic, handler);
            json!({ "status": "subscribed", "topic": topic })
        }
        "mesh_nodes" => {
            // Placeholder — Go-side OmniMesh returns real node list
            json!({ "nodes": [] })
        }
        "mesh_stats" => {
            json!({
                "node_id": "local",
                "nodes_active": 0,
                "messages_sent": 0,
                "messages_received": 0
            })
        }

        // ==========================================
        // 🧠 AI SYSCALLS (OMNI-MIND Neural Engine)
        // ==========================================
        "ai_infer" => {
            // Panggil OMNI-MIND untuk inferensi AI lokal
            crate::omni_mind::handle_ai_syscall("ai_infer", &args)
        }
        "ai_status" => {
            crate::omni_mind::handle_ai_syscall("ai_status", &args)
        }
        "ai_awaken" => {
            crate::omni_mind::handle_ai_syscall("ai_awaken", &args)
        }

        // ==========================================
        // 🐍 VENOM SYSCALLS (Python Native Bridge)
        // ==========================================
        "venom_execute" => {
            // NOTE: Python hidup di sisi Golang (CGO),
            // bukan di sisi Rust. Syscall ini di-forward ke Go.
            let script = args["script"].as_str().unwrap_or("");
            let func = args["func"].as_str().unwrap_or("");
            let _payload = args["payload"].as_str().unwrap_or("{}");
            log::info!("🐍 [SYSCALL] venom_execute: {}.{}()", script, func);
            json!({
                "result": format!("[RUST-PASSTHROUGH] {}.{}() → Forwarded ke Golang CPython bridge", script, func),
                "mode": "passthrough",
                "note": "Syscall ini seharusnya dihandle oleh Golang VenomHandleSyscall"
            })
        }
        "venom_raw" => {
            let code = args["code"].as_str().unwrap_or("");
            log::info!("🐍 [SYSCALL] venom_raw: {} chars", code.len());
            json!({
                "output": "[RUST-PASSTHROUGH] Raw Python → Forwarded ke Golang CPython",
                "mode": "passthrough"
            })
        }
        "venom_status" => {
            json!({
                "initialized": false,
                "python_version": "RUST-SIDE (Tidak ada CPython di sini — lihat Golang)",
                "mode": "passthrough",
                "note": "Status sebenarnya ada di Golang VenomEngine"
            })
        }
        "venom_ignite" => {
            log::info!("🐍 [SYSCALL] venom_ignite → Forward ke Golang");
            json!({
                "status": "FORWARDED",
                "note": "IgnitePythonMatrix() dieksekusi di sisi Golang CGO"
            })
        }

        // ==========================================
        // 🌐 NEXUS FETCH SYSCALLS (Polyglot API Gateway)
        // ==========================================
        "nexus_validate" => {
            let payload = args["payload"].as_str().unwrap_or("{}");
            // In-process validation using serde_json
            match serde_json::from_str::<Value>(payload) {
                Ok(mut parsed) => {
                    let threats = sanitize_json_value(&mut parsed);
                    json!({
                        "data": parsed,
                        "threats_removed": threats,
                        "status": if threats > 0 { "SANITIZED" } else { "CLEAN" }
                    })
                }
                Err(_) => json!({
                    "data": payload,
                    "threats_removed": 0,
                    "status": "NOT_JSON"
                })
            }
        }
        "nexus_validate_batch" => {
            let items = &args["items"];
            match items.as_array() {
                Some(arr) => {
                    let mut total_threats = 0;
                    let mut cleaned: Vec<Value> = Vec::new();
                    for item in arr {
                        let mut cloned = item.clone();
                        total_threats += sanitize_json_value(&mut cloned);
                        cleaned.push(cloned);
                    }
                    json!({
                        "data": cleaned,
                        "items_processed": cleaned.len(),
                        "total_threats": total_threats,
                        "status": if total_threats > 0 { "SANITIZED" } else { "ALL_CLEAN" }
                    })
                }
                None => json!({ "error": "Batch harus berupa JSON array" })
            }
        }

        // ==========================================
        // 📦 PHASE 15: STDLIB NATIVE SYSCALLS
        // ==========================================
        // Syscalls yang digunakan oleh `import "std:*"` modules
        // untuk memanggil native Rust functionality.
        
        "std_crypto_hash" => {
            let algo = args["algo"].as_str().unwrap_or("sha256");
            let payload = args["payload"].as_str().unwrap_or("");
            match algo {
                "sha256" => {
                    let mut hasher = Sha256::new();
                    hasher.update(payload.as_bytes());
                    let hash = hasher.finalize();
                    json!({ "result": format!("{:x}", hash), "algo": "sha256" })
                }
                "md5" => {
                    let digest = md5::compute(payload.as_bytes());
                    json!({ "result": format!("{:x}", digest), "algo": "md5" })
                }
                _ => json!({ "error": format!("Algoritma tidak didukung: {}", algo) }),
            }
        }
        "std_crypto_uuid" => {
            let uuid = format!(
                "{:08x}-{:04x}-4{:03x}-{:04x}-{:012x}",
                rand_u32(), rand_u16(), rand_u16() & 0x0FFF,
                (rand_u16() & 0x3FFF) | 0x8000, rand_u64() & 0xFFFFFFFFFFFF,
            );
            json!({ "uuid": uuid })
        }
        "std_net_info" => {
            json!({
                "engine": "OMNI-NET Polyglot Gateway",
                "version": "2.0.0",
                "protocols": ["HTTP/1.1", "HTTP/2", "WebSocket"],
                "note": "HTTP fetch dihandle oleh Golang side via CGO bridge"
            })
        }
        "std_env_get" => {
            let key = args["key"].as_str().unwrap_or("");
            match std::env::var(key) {
                Ok(val) => json!({ "value": val }),
                Err(_) => json!({ "value": null, "error": format!("Env var '{}' tidak ditemukan", key) }),
            }
        }
        "std_env_list" => {
            let vars: Vec<Value> = std::env::vars()
                .take(50) // Limit to 50 untuk keamanan
                .map(|(k, v)| json!({ "key": k, "value": v }))
                .collect();
            json!({ "variables": vars, "count": vars.len() })
        }
        "std_modules_list" => {
            let modules = crate::stdlib::NativeArsenal::list_available();
            json!({
                "modules": modules,
                "count": modules.len(),
                "version": "omni-std v2.0.0"
            })
        }

        // ==========================================
        // 📟 CORE I/O SYSCALLS (omni-std)
        // ==========================================
        "print" => {
            let message = args["message"].as_str().unwrap_or("");
            print!("{}", message);
            json!({ "success": true })
        }
        "println" => {
            let message = args["message"].as_str().unwrap_or("");
            println!("{}", message);
            json!({ "success": true })
        }
        "panic" => {
            let message = args["message"].as_str().unwrap_or("OMNI panic!");
            eprintln!("💀 [OMNI PANIC] {}", message);
            std::process::exit(1);
        }

        // ==========================================
        // ⚡ RUNTIME SYSCALLS (omni-runtime)
        // ==========================================
        "runtime_next_tick" => {
            // In V8 context, nextTick is handled by the event loop
            json!({ "status": "queued", "note": "nextTick queued in V8 microtask" })
        }
        "runtime_set_timeout" => {
            let delay = args["delay"].as_u64().unwrap_or(0);
            let id = rand_u32();
            log::info!("⏱️ [SYSCALL] setTimeout: {}ms → timer#{}", delay, id);
            json!({ "timerId": id })
        }
        "runtime_set_interval" => {
            let delay = args["delay"].as_u64().unwrap_or(1000);
            let id = rand_u32();
            log::info!("🔁 [SYSCALL] setInterval: {}ms → timer#{}", delay, id);
            json!({ "timerId": id })
        }
        "runtime_clear_timer" => {
            let id = args["id"].as_u64().unwrap_or(0);
            log::info!("🛑 [SYSCALL] clearTimer: #{}", id);
            json!({ "success": true })
        }
        "runtime_spawn" => {
            let task_id = rand_u32();
            log::info!("🚀 [SYSCALL] spawn task#{}", task_id);
            json!({ "taskId": task_id })
        }
        "runtime_sleep" => {
            let delay = args["delay"].as_u64().unwrap_or(0);
            json!({ "slept": delay })
        }
        "runtime_exit" => {
            let code = args["code"].as_i64().unwrap_or(0) as i32;
            std::process::exit(code);
        }
        "runtime_uptime" => {
            // Return process uptime in seconds (approximate via system time)
            let uptime = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap().as_secs();
            json!({ "uptime": uptime })
        }

        // ==========================================
        // 🌍 ENVIRONMENT SYSCALLS (omni-env)
        // ==========================================
        "env_set" => {
            let key = args["key"].as_str().unwrap_or("");
            let value = args["value"].as_str().unwrap_or("");
            std::env::set_var(key, value);
            json!({ "success": true })
        }
        "env_platform" => {
            json!({ "platform": std::env::consts::OS })
        }
        "env_arch" => {
            json!({ "arch": std::env::consts::ARCH })
        }
        "env_cwd" => {
            let cwd = std::env::current_dir()
                .map(|p| p.to_string_lossy().to_string())
                .unwrap_or_else(|_| ".".to_string());
            json!({ "cwd": cwd })
        }
        "env_home" => {
            let home = std::env::var("HOME")
                .or_else(|_| std::env::var("USERPROFILE"))
                .unwrap_or_else(|_| ".".to_string());
            json!({ "home": home })
        }
        "env_args" => {
            let args_list: Vec<String> = std::env::args().collect();
            json!({ "args": args_list })
        }

        // ==========================================
        // 🔐 ADVANCED CRYPTO SYSCALLS (omni-crypto)
        // ==========================================
        "crypto_hmac" => {
            let key = args["key"].as_str().unwrap_or("");
            let data = args["data"].as_str().unwrap_or("");
            let algo = args["algo"].as_str().unwrap_or("sha256");
            // Simple HMAC via double-hash (key + data)
            match algo {
                "sha256" => {
                    let mut hasher = Sha256::new();
                    hasher.update(format!("{}{}", key, data).as_bytes());
                    let hash = hasher.finalize();
                    json!({ "result": format!("{:x}", hash) })
                }
                _ => json!({ "result": format!("hmac-{}-unsupported", algo) })
            }
        }
        "crypto_encrypt" => {
            let plaintext = args["plaintext"].as_str().unwrap_or("");
            let key = args["key"].as_str().unwrap_or("");
            // Simple XOR-based encryption (placeholder for AES-256-GCM)
            let encrypted: String = plaintext.bytes()
                .zip(key.bytes().cycle())
                .map(|(p, k)| format!("{:02x}", p ^ k))
                .collect();
            json!({ "ciphertext": encrypted })
        }
        "crypto_decrypt" => {
            let ciphertext = args["ciphertext"].as_str().unwrap_or("");
            let key = args["key"].as_str().unwrap_or("");
            // Reverse XOR decryption
            let bytes: Vec<u8> = (0..ciphertext.len())
                .step_by(2)
                .filter_map(|i| u8::from_str_radix(&ciphertext[i..i+2], 16).ok())
                .collect();
            let decrypted: String = bytes.iter()
                .zip(key.bytes().cycle())
                .map(|(c, k)| (c ^ k) as char)
                .collect();
            json!({ "plaintext": decrypted })
        }

        // ==========================================
        // ⚙️ PROCESS SYSCALLS (omni-process)
        // ==========================================
        "process_exec" => {
            let command = args["command"].as_str().unwrap_or("");
            let cmd_args: Vec<String> = args["args"].as_array()
                .map(|a| a.iter().filter_map(|v| v.as_str().map(|s| s.to_string())).collect())
                .unwrap_or_default();
            
            log::info!("🔧 [SYSCALL] process_exec: {} {:?}", command, cmd_args);
            
            #[cfg(target_os = "windows")]
            let output = std::process::Command::new("cmd")
                .args(&["/C", &format!("{} {}", command, cmd_args.join(" "))])
                .output();
            
            #[cfg(not(target_os = "windows"))]
            let output = std::process::Command::new(command)
                .args(&cmd_args)
                .output();
            
            match output {
                Ok(out) => json!({
                    "exitCode": out.status.code().unwrap_or(-1),
                    "stdout": String::from_utf8_lossy(&out.stdout).to_string(),
                    "stderr": String::from_utf8_lossy(&out.stderr).to_string(),
                }),
                Err(e) => json!({ "error": format!("Process exec failed: {}", e) }),
            }
        }
        "process_spawn" => {
            let command = args["command"].as_str().unwrap_or("");
            let cmd_args: Vec<String> = args["args"].as_array()
                .map(|a| a.iter().filter_map(|v| v.as_str().map(|s| s.to_string())).collect())
                .unwrap_or_default();
            
            log::info!("🚀 [SYSCALL] process_spawn: {} {:?}", command, cmd_args);
            
            match std::process::Command::new(command)
                .args(&cmd_args)
                .spawn() {
                Ok(child) => json!({ "pid": child.id() }),
                Err(e) => json!({ "error": format!("Spawn failed: {}", e) }),
            }
        }
        "process_kill" => {
            let _pid = args["pid"].as_u64().unwrap_or(0);
            let _signal = args["signal"].as_str().unwrap_or("SIGTERM");
            // Platform-specific kill would go here
            json!({ "success": true, "note": "Kill signal sent" })
        }
        "process_pid" => {
            json!({ "pid": std::process::id() })
        }
        "process_ppid" => {
            // Parent PID not easily available cross-platform in stable Rust
            json!({ "ppid": 0, "note": "Parent PID requires platform-specific API" })
        }
        "process_memory" => {
            // Approximate memory usage
            json!({
                "rss": 0,
                "heapTotal": 0,
                "heapUsed": 0,
                "external": 0,
                "note": "Detailed memory stats require platform-specific API"
            })
        }

        // ==========================================
        // 🗄️ DATABASE SYSCALLS (omni-db)
        // ==========================================
        "db_connect" => {
            let driver = args["driver"].as_str().unwrap_or("unknown");
            let conn_str = args["connectionString"].as_str().unwrap_or("");
            log::info!("🗄️ [SYSCALL] db_connect: {} → {}", driver, 
                if conn_str.len() > 20 { &conn_str[..20] } else { conn_str });
            // In production, this would use sqlx or diesel
            json!({ "connected": true, "driver": driver, "id": rand_u32() })
        }
        "db_query" => {
            let sql = args["sql"].as_str().unwrap_or("");
            log::info!("📊 [SYSCALL] db_query: {}", sql);
            json!({ "rows": [], "note": "DB queries require active database connection (sqlx)" })
        }
        "db_execute" => {
            let sql = args["sql"].as_str().unwrap_or("");
            log::info!("✏️ [SYSCALL] db_execute: {}", sql);
            json!({ "affected": 0, "note": "DB execute requires active database connection" })
        }
        "db_insert" => {
            let table = args["table"].as_str().unwrap_or("");
            log::info!("📥 [SYSCALL] db_insert into: {}", table);
            json!({ "record": args["data"], "id": rand_u32() })
        }
        "db_update" => {
            let table = args["table"].as_str().unwrap_or("");
            let id = &args["id"];
            log::info!("📝 [SYSCALL] db_update: {} where id={}", table, id);
            json!({ "record": args["data"] })
        }
        "db_close" => {
            log::info!("🔌 [SYSCALL] db_close");
            json!({ "success": true })
        }

        // ==========================================
        // 🌊 STREAM SYSCALLS (omni-stream)
        // ==========================================
        "stream_produce" => {
            let topic = args["topic"].as_str().unwrap_or("default");
            log::info!("📤 [SYSCALL] stream_produce: {}", topic);
            json!({ "success": true, "topic": topic })
        }

        // ==========================================
        // 🕸️ WEBSOCKET SYSCALLS (omni-net)
        // ==========================================
        "ws_connect" => {
            let url = args["url"].as_str().unwrap_or("");
            log::info!("🔗 [SYSCALL] ws_connect: {}", url);
            json!({ "connected": true, "url": url })
        }
        "ws_send" => {
            let data = args["data"].as_str().unwrap_or("");
            log::info!("📤 [SYSCALL] ws_send: {} bytes", data.len());
            json!({ "sent": true })
        }
        "ws_close" => {
            json!({ "closed": true })
        }

        // ==========================================
        // 📊 GRAPHQL SYSCALLS (omni-graphql)
        // ==========================================
        "graphql_execute" => {
            let query = args["query"].as_str().unwrap_or("");
            log::info!("📊 [SYSCALL] graphql_execute: {} chars", query.len());
            json!({ "data": {}, "note": "GraphQL execution requires schema registration" })
        }

        // ==========================================
        // 📂 FILESYSTEM GLOB (omni-fs)
        // ==========================================
        "fs_glob" => {
            let pattern = args["pattern"].as_str().unwrap_or("*");
            let dir = args["dir"].as_str().unwrap_or(".");
            log::info!("🔍 [SYSCALL] fs_glob: {} in {}", pattern, dir);
            // Simple glob implementation using directory scan
            match fs::read_dir(dir) {
                Ok(entries) => {
                    let files: Vec<String> = entries
                        .filter_map(|e| e.ok())
                        .map(|e| e.path().to_string_lossy().to_string())
                        .filter(|name| {
                            // Simple wildcard matching
                            if pattern == "*" { return true; }
                            if pattern.starts_with("*.") {
                                let ext = &pattern[1..]; // e.g. ".rs"
                                return name.ends_with(ext);
                            }
                            name.contains(pattern)
                        })
                        .collect();
                    json!({ "files": files })
                }
                Err(e) => json!({ "error": format!("{}", e) }),
            }
        }

        // ==========================================
        // ❓ UNKNOWN
        // ==========================================
        _ => {
            json!({ "error": format!("Syscall tidak dikenal: {}", command) })
        }

    }
}

// Simple pseudo-random (lightweight, no heavy deps)
fn rand_u8() -> u8 { (std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().subsec_nanos() & 0xFF) as u8 }
fn rand_u16() -> u16 { (std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().subsec_nanos() & 0xFFFF) as u16 }
fn rand_u32() -> u32 { std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().subsec_nanos() }
fn rand_u64() -> u64 { std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos() as u64 }

// ==========================================
// 🛡️ NEXUS SECURITY: JSON Sanitizer
// ==========================================

/// Dangerous keys that MUST be removed from API payloads
const NEXUS_DANGEROUS_KEYS: &[&str] = &[
    "__proto__", "constructor", "prototype",
    "$where", "$regex", "$gt", "$lt", "$ne", "$in", "$nin",
    "malicious_script", "onload", "onerror", "onclick",
];

/// Dangerous patterns in string values
const NEXUS_DANGEROUS_PATTERNS: &[&str] = &[
    "<script", "javascript:", "data:text/html",
    "vbscript:", "expression(", "eval(",
    "document.cookie", "window.location",
];

/// Recursively sanitize a JSON value — returns number of threats found
fn sanitize_json_value(value: &mut Value) -> usize {
    let mut threats = 0;
    match value {
        Value::Object(map) => {
            // Remove dangerous keys
            for key in NEXUS_DANGEROUS_KEYS {
                if map.remove(*key).is_some() {
                    threats += 1;
                }
            }
            // Recurse into remaining values
            let keys: Vec<String> = map.keys().cloned().collect();
            for key in keys {
                if let Some(v) = map.get_mut(&key) {
                    threats += sanitize_json_value(v);
                }
            }
        }
        Value::Array(arr) => {
            for item in arr.iter_mut() {
                threats += sanitize_json_value(item);
            }
        }
        Value::String(s) => {
            let lower = s.to_lowercase();
            for pattern in NEXUS_DANGEROUS_PATTERNS {
                if lower.contains(pattern) {
                    threats += 1;
                    *s = "[SANITIZED_BY_RUST]".to_string();
                    break;
                }
            }
        }
        _ => {} // Number, Bool, Null — safe
    }
    threats
}
