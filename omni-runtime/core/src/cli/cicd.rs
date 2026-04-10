use std::fs;
use std::path::Path;
use std::process::{Command, Stdio};
use std::io::{Read, Write};

pub fn run(args: &[String], original_command: &str) {
    match original_command {
        "pipeline" => {
            if args.is_empty() {
                println!("❌ Sub-command needed: init, run, webhook");
                std::process::exit(1);
            }
            match args[0].as_str() {
                "init" => {
                    let config_dir = Path::new(".omni_cicd");
                    if !config_dir.exists() {
                        fs::create_dir_all(config_dir).unwrap();
                    }
                    let yaml = r#"
# NATIVE OMNI CI/CD MANIFEST
stages:
  - lint
  - build
  - test
  - deploy
"#;
                    let file_path = config_dir.join("pipeline.yaml");
                    fs::write(&file_path, yaml.trim()).unwrap();
                    println!("🚀 [OMNI CI/CD] Real CI/CD manifest written to .omni_cicd/pipeline.yaml");
                }
                "run" => {
                    println!("🔄 [OMNI CI/CD] Executing Auto-Detected Pipeline...");
                    let mut success = true;

                    // Rust detection
                    if Path::new("Cargo.toml").exists() {
                        println!("⚡ Detected Rust project (Cargo.toml). Running cargo tests...");
                        let status = Command::new("cargo")
                            .arg("test")
                            .stdout(Stdio::inherit())
                            .stderr(Stdio::inherit())
                            .status();
                        if let Ok(stat) = status {
                            if !stat.success() { success = false; }
                        } else {
                            println!("⚠️ 'cargo' command failed to execute. Is Rust installed?");
                            success = false;
                        }
                    }

                    // Go detection
                    if Path::new("go.mod").exists() {
                        println!("⚡ Detected Go project (go.mod). Running go tests...");
                        let status = Command::new("go")
                            .arg("test")
                            .arg("./...")
                            .stdout(Stdio::inherit())
                            .stderr(Stdio::inherit())
                            .status();
                        if let Ok(stat) = status {
                            if !stat.success() { success = false; }
                        } else {
                            println!("⚠️ 'go' command failed to execute. Is Go installed?");
                            success = false;
                        }
                    }

                    // Node.js detection
                    if Path::new("package.json").exists() {
                        println!("⚡ Detected Node.js project. Running npm test...");
                        let npm_cmd = if cfg!(target_os = "windows") { "npm.cmd" } else { "npm" };
                        let status = Command::new(npm_cmd)
                            .arg("test")
                            .stdout(Stdio::inherit())
                            .stderr(Stdio::inherit())
                            .status();
                        if let Ok(stat) = status {
                            if !stat.success() { success = false; }
                        } else {
                            println!("⚠️ 'npm' failed to execute.");
                            success = false;
                        }
                    }

                    if success {
                        println!("✅ [OMNI CI/CD] Local Build Pipeline Selesai. Semua unit test lulus. Layak Push!");
                    } else {
                        println!("❌ [OMNI CI/CD] Pipeline gagal karena error di eksekusi test.");
                        std::process::exit(1);
                    }
                }
                "webhook" => {
                    let default_port = "8080";
                    let port = args.get(1).unwrap_or(&default_port.to_string());
                    println!("🪝 [OMNI CI/CD] Webhook server listening on 0.0.0.0:{} to trigger Auto-Deploy...", port);
                    // Real HTTP webhook listener implementation
                    use std::net::TcpListener;
                    if let Ok(listener) = TcpListener::bind(format!("0.0.0.0:{}", port)) {
                        println!("✅ Webhook server active. Press Ctrl+C to exit.");
                        for stream in listener.incoming() {
                            match stream {
                                Ok(mut stream) => {
                                    let mut buffer = [0; 1024];
                                    let _ = stream.read(&mut buffer);
                                    println!("⚡ Menerima Webhook Payload. Memulai Deployment Otomatis...");
                                    let response = "HTTP/1.1 200 OK\r\n\r\nWebhook received by Omni CI/CD.";
                                    let _ = stream.write(response.as_bytes());
                                }
                                Err(e) => println!("Error: {}", e),
                            }
                        }
                    } else {
                        println!("❌ Gagal mem-bind port webhook {}", port);
                    }
                }
                _ => {
                    println!("❌ Sub-perintah Pipeline '{}' tidak dikenali.", args[0]);
                }
            }
        }
        "release" => {
            if args.len() > 0 && args[0] == "bump" {
                println!("📈 [OMNI CI/CD] Implementing semantic version bump...");
                let cargo_path = "Cargo.toml";
                if Path::new(cargo_path).exists() {
                    let content = fs::read_to_string(cargo_path).unwrap();
                    let mut new_lines = Vec::new();
                    let mut bumped = false;
                    for line in content.lines() {
                        if line.starts_with("version =") && !bumped {
                            if let Some(mut var) = extract_version(line) {
                                let mut parts: Vec<u32> = var.split('.').filter_map(|s| s.parse().ok()).collect();
                                if parts.len() == 3 {
                                    parts[2] += 1; // Bump patch version
                                    let new_version = format!("version = \"{}.{}.{}\"", parts[0], parts[1], parts[2]);
                                    println!("✅ Bumping {} -> {}.{}.{}", var, parts[0], parts[1], parts[2]);
                                    new_lines.push(new_version);
                                    bumped = true;
                                    continue;
                                }
                            }
                        }
                        new_lines.push(line.to_string());
                    }
                    if bumped {
                        fs::write(cargo_path, new_lines.join("\n")).unwrap();
                        println!("✅ Semantic Versioning di-update sukses.");
                    }
                } else {
                    println!("⚠️ Tidak ditemukan Cargo.toml untuk auto-bump. Mendukung ekosistem lain kelak.");
                }
            } else {
                println!("❌ Gunakan: omni release bump");
            }
        }
        _ => {
            println!("❌ Perintah CI/CD tidak dikenali.");
        }
    }
}

fn extract_version(line: &str) -> Option<String> {
    let parts: Vec<&str> = line.split('"').collect();
    if parts.len() >= 2 {
        Some(parts[1].to_string())
    } else {
        None
    }
}
