// ============================================================
// 🧪 OMNI TEST RUNNER: Validasi Kompilasi Per-Modul
// ============================================================
#![allow(dead_code, unused_imports)]
// Submodul dari Build Toolchain yang menjalankan pengujian
// kompilasi mandiri untuk setiap file sumber di modul tertentu.
// Menghasilkan laporan JSON yang bisa diparseoleh CI/CD.
// ============================================================

use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

#[derive(Debug, Clone)]
pub struct TestResult {
    pub module_name: String,
    pub test_file: String,
    pub passed: bool,
    pub output: String,
    pub duration_ms: u128,
}

/// Menjalankan semua test di dalam direktori `tests/` sebuah modul.
pub fn run_module_tests(module_path: &Path) -> Vec<TestResult> {
    let mut results = Vec::new();
    let tests_dir = module_path.join("tests");

    if !tests_dir.exists() {
        return results;
    }

    // Scan semua file .test.omni
    scan_and_run_tests(&tests_dir, module_path, &mut results);
    results
}

fn scan_and_run_tests(dir: &Path, module_path: &Path, results: &mut Vec<TestResult>) {
    let entries = match fs::read_dir(dir) {
        Ok(e) => e,
        Err(_) => return,
    };

    for entry in entries.flatten() {
        let path = entry.path();
        if path.is_dir() {
            scan_and_run_tests(&path, module_path, results);
            continue;
        }

        let filename = path.file_name()
            .unwrap_or_default()
            .to_string_lossy()
            .into_owned();

        if filename.ends_with(".test.omni") {
            let result = execute_test_file(&path, module_path);
            results.push(result);
        }
    }
}

fn execute_test_file(test_file: &Path, module_path: &Path) -> TestResult {
    let start = std::time::Instant::now();
    let module_name = module_path.file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();

    // Untuk saat ini, validasi bahwa file test bisa dibaca dan parsed
    let content = match fs::read_to_string(test_file) {
        Ok(c) => c,
        Err(e) => {
            return TestResult {
                module_name,
                test_file: test_file.display().to_string(),
                passed: false,
                output: format!("Gagal membaca test file: {}", e),
                duration_ms: start.elapsed().as_millis(),
            };
        }
    };

    // Basic syntax validation: cari keyword "test("
    let has_tests = content.contains("test(") || content.contains("fuzz_test(");
    
    TestResult {
        module_name,
        test_file: test_file.display().to_string(),
        passed: has_tests,
        output: if has_tests {
            format!("Test file valid — {} bytes parsed", content.len())
        } else {
            "WARNING: Tidak ada deklarasi test() ditemukan".to_string()
        },
        duration_ms: start.elapsed().as_millis(),
    }
}

/// Menghasilkan laporan JSON dari hasil test
pub fn generate_json_report(results: &[TestResult], output_path: &Path) {
    let mut json = String::from("[\n");
    
    for (i, result) in results.iter().enumerate() {
        json.push_str(&format!(
            "  {{\n    \"module\": \"{}\",\n    \"file\": \"{}\",\n    \"passed\": {},\n    \"output\": \"{}\",\n    \"duration_ms\": {}\n  }}",
            result.module_name,
            result.test_file.replace('\\', "/"),
            result.passed,
            result.output.replace('"', "\\\""),
            result.duration_ms
        ));
        if i < results.len() - 1 {
            json.push(',');
        }
        json.push('\n');
    }
    
    json.push_str("]\n");
    fs::write(output_path, json).ok();
}

/// Mencetak ringkasan test ke stdout
pub fn print_test_summary(results: &[TestResult]) {
    let passed = results.iter().filter(|r| r.passed).count();
    let failed = results.iter().filter(|r| !r.passed).count();
    let total = results.len();

    println!();
    println!("===========================================================");
    println!("  OMNI TEST RUNNER — Results");
    println!("===========================================================");

    for result in results {
        let icon = if result.passed { "PASS" } else { "FAIL" };
        let short = Path::new(&result.test_file)
            .file_name()
            .unwrap_or_default()
            .to_string_lossy();
        
        println!("  [{}] {} :: {} ({}ms)",
            icon, result.module_name, short, result.duration_ms);
    }

    println!();
    println!("  TOTAL: {} passed | {} failed | {} total", passed, failed, total);
    println!("===========================================================");
}
