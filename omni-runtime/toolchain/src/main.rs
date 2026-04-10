// ============================================================
// 🔨 OMNI BUILD TOOLCHAIN: Multi-Language Compilation Orchestrator
// ============================================================
#![allow(dead_code, unused_imports)]
// Binary utama yang mengorkestrasi kompilasi C, C++, Rust, dan Go
// di seluruh modul omni_modules. Ini adalah jantung dari
// `omni build` command.
//
// Alur kerja:
//   1. Scan semua modul di omni_modules/
//   2. Untuk setiap modul, identifikasi file sumber per bahasa
//   3. Panggil compiler yang tepat (gcc, g++, rustc, go build)
//   4. Kumpulkan .o/.rlib/.a object files
//   5. Laporkan hasil: PASS / FAIL / SKIP per modul
// ============================================================

use std::collections::HashMap;
use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::Instant;

mod test_runner;

// ============================================================
// Tipe Data Inti
// ============================================================

#[derive(Debug, Clone)]
struct ModuleInfo {
    name: String,
    path: PathBuf,
    c_files: Vec<PathBuf>,
    cpp_files: Vec<PathBuf>,
    rs_files: Vec<PathBuf>,
    go_files: Vec<PathBuf>,
}

#[derive(Debug, Clone)]
enum CompileStatus {
    Pass,
    Fail(String),
    Skip(String),
}

#[derive(Debug)]
struct CompileReport {
    module: String,
    language: String,
    file: String,
    status: CompileStatus,
    duration_ms: u128,
}

// ============================================================
// Scanner: Menemukan semua modul dan file sumber
// ============================================================

fn scan_modules(modules_dir: &Path) -> Vec<ModuleInfo> {
    let mut modules = Vec::new();
    
    let entries = match fs::read_dir(modules_dir) {
        Ok(e) => e,
        Err(err) => {
            eprintln!("FATAL: Tidak bisa membaca {}: {}", modules_dir.display(), err);
            return modules;
        }
    };

    for entry in entries.flatten() {
        let path = entry.path();
        if !path.is_dir() { continue; }
        
        let name = path.file_name()
            .unwrap_or_default()
            .to_string_lossy()
            .into_owned();

        let mut module = ModuleInfo {
            name,
            path: path.clone(),
            c_files: Vec::new(),
            cpp_files: Vec::new(),
            rs_files: Vec::new(),
            go_files: Vec::new(),
        };

        // Scan rekursif untuk file sumber
        scan_source_files(&path, &mut module);
        modules.push(module);
    }

    modules.sort_by(|a, b| a.name.cmp(&b.name));
    modules
}

fn scan_source_files(dir: &Path, module: &mut ModuleInfo) {
    let entries = match fs::read_dir(dir) {
        Ok(e) => e,
        Err(_) => return,
    };

    for entry in entries.flatten() {
        let path = entry.path();
        if path.is_dir() {
            scan_source_files(&path, module);
            continue;
        }

        match path.extension().and_then(|e| e.to_str()) {
            Some("c")   => module.c_files.push(path),
            Some("cpp") => module.cpp_files.push(path),
            Some("rs")  => module.rs_files.push(path),
            Some("go")  => module.go_files.push(path),
            _ => {}
        }
    }
}

// ============================================================
// Compiler Invocations
// ============================================================

fn compile_c_file(file: &Path, output_dir: &Path, is_release: bool) -> CompileReport {
    let start = Instant::now();
    let stem = file.file_stem().unwrap_or_default().to_string_lossy();
    let out_file = output_dir.join(format!("{}.o", stem));

    let mut cmd = Command::new("gcc");
    cmd.arg("-c")
       .arg("-Wall")
       .arg("-Wextra")
       .arg("-std=c11")
       .arg("-fPIC");

    if is_release {
        cmd.arg("-O3").arg("-DNDEBUG");
    } else {
        cmd.arg("-g").arg("-O0");
    }

    cmd.arg(file)
       .arg("-o")
       .arg(&out_file);

    let status = match cmd.output() {
        Ok(output) => {
            if output.status.success() {
                CompileStatus::Pass
            } else {
                CompileStatus::Fail(
                    String::from_utf8_lossy(&output.stderr).into_owned()
                )
            }
        }
        Err(e) => CompileStatus::Skip(format!("gcc not found: {}", e)),
    };

    CompileReport {
        module: String::new(),
        language: "C".to_string(),
        file: file.display().to_string(),
        status,
        duration_ms: start.elapsed().as_millis(),
    }
}

fn compile_cpp_file(file: &Path, output_dir: &Path, is_release: bool) -> CompileReport {
    let start = Instant::now();
    let stem = file.file_stem().unwrap_or_default().to_string_lossy();
    let out_file = output_dir.join(format!("{}.o", stem));

    let mut cmd = Command::new("g++");
    cmd.arg("-c")
       .arg("-Wall")
       .arg("-std=c++17")
       .arg("-fPIC");

    if is_release { cmd.arg("-O3"); } else { cmd.arg("-g"); }

    cmd.arg(file).arg("-o").arg(&out_file);

    let status = match cmd.output() {
        Ok(output) => {
            if output.status.success() {
                CompileStatus::Pass
            } else {
                CompileStatus::Fail(String::from_utf8_lossy(&output.stderr).into_owned())
            }
        }
        Err(e) => CompileStatus::Skip(format!("g++ not found: {}", e)),
    };

    CompileReport {
        module: String::new(),
        language: "C++".to_string(),
        file: file.display().to_string(),
        status,
        duration_ms: start.elapsed().as_millis(),
    }
}

fn compile_rs_file(file: &Path, output_dir: &Path, is_release: bool) -> CompileReport {
    let start = Instant::now();
    let stem = file.file_stem().unwrap_or_default().to_string_lossy();
    let out_file = output_dir.join(format!("lib{}.rlib", stem));

    let mut cmd = Command::new("rustc");
    cmd.arg("--edition").arg("2021")
       .arg("--crate-type").arg("lib");

    if is_release {
        cmd.arg("-C").arg("opt-level=3");
    }

    cmd.arg(file).arg("-o").arg(&out_file);

    let status = match cmd.output() {
        Ok(output) => {
            if output.status.success() {
                CompileStatus::Pass
            } else {
                CompileStatus::Fail(String::from_utf8_lossy(&output.stderr).into_owned())
            }
        }
        Err(e) => CompileStatus::Skip(format!("rustc not found: {}", e)),
    };

    CompileReport {
        module: String::new(),
        language: "Rust".to_string(),
        file: file.display().to_string(),
        status,
        duration_ms: start.elapsed().as_millis(),
    }
}

fn check_go_syntax(file: &Path) -> CompileReport {
    let start = Instant::now();

    let mut cmd = Command::new("go");
    cmd.arg("vet").arg(file);

    let status = match cmd.output() {
        Ok(output) => {
            if output.status.success() {
                CompileStatus::Pass
            } else {
                CompileStatus::Fail(String::from_utf8_lossy(&output.stderr).into_owned())
            }
        }
        Err(e) => CompileStatus::Skip(format!("go not found: {}", e)),
    };

    CompileReport {
        module: String::new(),
        language: "Go".to_string(),
        file: file.display().to_string(),
        status,
        duration_ms: start.elapsed().as_millis(),
    }
}

// ============================================================
// Build Orchestrator
// ============================================================

fn build_module(module: &ModuleInfo, output_base: &Path, is_release: bool) -> Vec<CompileReport> {
    let mut reports = Vec::new();
    let module_output = output_base.join(&module.name);
    fs::create_dir_all(&module_output).ok();

    // Compile C files
    for file in &module.c_files {
        let mut report = compile_c_file(file, &module_output, is_release);
        report.module = module.name.clone();
        reports.push(report);
    }

    // Compile C++ files
    for file in &module.cpp_files {
        let mut report = compile_cpp_file(file, &module_output, is_release);
        report.module = module.name.clone();
        reports.push(report);
    }

    // Compile Rust files
    for file in &module.rs_files {
        let mut report = compile_rs_file(file, &module_output, is_release);
        report.module = module.name.clone();
        reports.push(report);
    }

    // Check Go syntax
    for file in &module.go_files {
        let mut report = check_go_syntax(file);
        report.module = module.name.clone();
        reports.push(report);
    }

    reports
}

// ============================================================
// Report Generator
// ============================================================

fn print_report(reports: &[CompileReport]) {
    let mut pass_count = 0;
    let mut fail_count = 0;
    let mut skip_count = 0;

    println!();
    println!("===========================================================");
    println!("  OMNI BUILD TOOLCHAIN — Compilation Report");
    println!("===========================================================");

    let mut current_module = String::new();
    for report in reports {
        if report.module != current_module {
            current_module = report.module.clone();
            println!();
            println!("--- {} ---", current_module);
        }

        let (icon, label) = match &report.status {
            CompileStatus::Pass => { pass_count += 1; ("PASS", "") }
            CompileStatus::Fail(msg) => { fail_count += 1; ("FAIL", msg.as_str()) }
            CompileStatus::Skip(msg) => { skip_count += 1; ("SKIP", msg.as_str()) }
        };

        let short_file = Path::new(&report.file)
            .file_name()
            .unwrap_or_default()
            .to_string_lossy();

        println!("  [{}] {:>4} | {} | {}ms",
            icon, report.language, short_file, report.duration_ms);
        
        if !label.is_empty() {
            // Truncate error message for display
            let truncated: String = label.chars().take(120).collect();
            println!("         > {}", truncated);
        }
    }

    println!();
    println!("===========================================================");
    println!("  TOTAL: {} pass | {} fail | {} skip", pass_count, fail_count, skip_count);
    println!("===========================================================");
}

// ============================================================
// Main Entry Point
// ============================================================

fn main() {
    let args: Vec<String> = env::args().collect();
    let is_release = args.contains(&"--release".to_string());
    let single_module = args.iter()
        .position(|a| a == "--module")
        .and_then(|i| args.get(i + 1))
        .cloned();

    println!("=========================================");
    println!("  OMNI BUILD TOOLCHAIN v1.0.0");
    println!("  Mode: {}", if is_release { "RELEASE" } else { "DEBUG" });
    println!("=========================================");

    // Determine paths
    let toolchain_dir = env::current_dir().unwrap_or_default();
    let modules_dir = toolchain_dir.parent()
        .map(|p| p.join("omni_modules"))
        .unwrap_or_else(|| PathBuf::from("../omni_modules"));
    let output_dir = toolchain_dir.parent()
        .map(|p| p.join("target").join("modules"))
        .unwrap_or_else(|| PathBuf::from("../target/modules"));

    fs::create_dir_all(&output_dir).ok();

    // Scan modules
    let modules = scan_modules(&modules_dir);
    println!("Found {} modules in {}", modules.len(), modules_dir.display());

    // Filter jika --module diberikan
    let targets: Vec<&ModuleInfo> = if let Some(ref name) = single_module {
        modules.iter().filter(|m| m.name == *name).collect()
    } else {
        modules.iter().collect()
    };

    // Build all targets
    let start = Instant::now();
    let mut all_reports = Vec::new();

    for module in &targets {
        let source_count = module.c_files.len() 
            + module.cpp_files.len() 
            + module.rs_files.len() 
            + module.go_files.len();
        
        if source_count == 0 { continue; }

        println!("Building: {} ({} sources)", module.name, source_count);
        let reports = build_module(module, &output_dir, is_release);
        all_reports.extend(reports);
    }

    let total_time = start.elapsed();

    // Print final report
    print_report(&all_reports);
    println!("  Total time: {:.2}s", total_time.as_secs_f64());
    println!("=========================================");
}
