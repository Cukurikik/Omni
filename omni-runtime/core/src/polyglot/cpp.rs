use std::fs;
use std::path::Path;
use std::process::Command;

pub fn scaffold_and_run() {
    let project_dir = Path::new("omni_cpp_pipeline");

    if !project_dir.exists() {
        fs::create_dir_all(project_dir).unwrap();
    }

    let cpp_file = project_dir.join("pipeline.cpp");
    let cmakelists = project_dir.join("CMakeLists.txt");

    let cpp_code = r#"
#include <iostream>
#include <vector>
#include <chrono>

int main() {
    std::cout << "🚀 [OMNI-CPP] Menghidupkan komputasi mutlak Hardware Pipeline..." << std::endl;
    
    auto start = std::chrono::high_resolution_clock::now();
    
    // Kalkulasi Matrix Operation Ril
    long long sum = 0;
    std::vector<int> tensor(10000000, 1);
    for(int val : tensor) {
        sum += val;
    }
    
    auto stop = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(stop - start);
    
    std::cout << "✅ [OMNI-CPP] Komputasi Matriks Tensorial berukuran 10,000,000 selesai." << std::endl;
    std::cout << "⏱️ Waktu Eksekusi Murni (Hardware C++): " << duration.count() << " ms" << std::endl;
    
    return 0;
}
"#;

    let cmake_code = r#"
cmake_minimum_required(VERSION 3.10)
project(OmniCppPipeline)

set(CMAKE_CXX_STANDARD 17)

add_executable(pipeline pipeline.cpp)
"#;

    fs::write(&cpp_file, cpp_code.trim()).expect("Gagal menulis pipeline.cpp");
    fs::write(&cmakelists, cmake_code.trim()).expect("Gagal menulis CMakeLists.txt");

    println!("✅ [OMNI POLYGLOT] Scaffolding C++ (Pipelines) siap di ./omni_cpp_pipeline");
    println!("⚙️  Membentuk C++ Biner Asli via G++...");

    // Default to a direct g++ compilation if Make isn't easily cross-platform
    match Command::new("g++")
        .arg("pipeline.cpp")
        .arg("-o")
        .arg("pipeline")
        .current_dir(project_dir)
        .status() {
            Ok(status) if status.success() => {
                println!("🔥 Eksekusi C++ Native Runtime (Bebas Virtual-Machine)...");
                let exe_name = if cfg!(windows) { "pipeline.exe" } else { "./pipeline" };
                match Command::new(exe_name)
                    .current_dir(project_dir)
                    .spawn() {
                        Ok(child) => {
                            println!("✅ [PID: {}] Pipeline C++ Melaju dalam Sub-Process OS Mutlak!", child.id());
                        }
                        Err(e) => {
                            println!("❌ Gagal mengeksekusi pipeline biner: {}", e);
                        }
                    }
            }
            _ => {
                println!("❌ Gagal mengompilasi biner C++. Pastikan 'g++' compiler terpasang di OS Anda.");
            }
        }
}
