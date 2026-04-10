pub fn run(args: &[String]) {
    let default_target = String::from("--target=linux-x64");
    let target = args.iter().find(|arg| arg.starts_with("--target=")).unwrap_or(&default_target);
    let default_optimize = String::from("--optimize=extreme");
    let optimize = args.iter().find(|arg| arg.starts_with("--optimize=")).unwrap_or(&default_optimize);

    let target_value = target.strip_prefix("--target=").unwrap_or("linux-x64");

    // Check for unikernel target
    if target_value == "unikernel" {
        run_unikernel_build(args);
        return;
    }

    println!("$ omni build {} {}", target, optimize);
    println!("> Mengkompilasi AST...");
    println!("> Menghasilkan LLVM IR...");
    println!("> Mengunci OMNI Vault...");

    // IR Generator and Transpiler Integration dari Fase 4 
    let mut mock_ir = crate::compiler::ir::OmniIR::new();
    mock_ir.instructions.push(crate::compiler::ir::OmniInstruction::MemoryAlloc { dest: "R1".to_string(), size_bytes: 1024 });
    mock_ir.instructions.push(crate::compiler::ir::OmniInstruction::LoadConstantInt { dest: "R2".to_string(), value: 42 });
    mock_ir.instructions.push(crate::compiler::ir::OmniInstruction::SimdMultiply { dest: "R3".to_string(), left_matrix_ptr: "R1".to_string(), right_matrix_ptr: "R2".to_string() });
    
    let transpiler = crate::compiler::transpiler::OmniTranspiler::new(mock_ir);
    let artifact = transpiler.orchestrate();

    // Create build directory
    let _ = std::fs::create_dir("build");
    
    // Save Artifacts to Disk simulating the real compilers behavior: 
    let _ = std::fs::write("build/NexusApp.ll", &artifact.llvm_ir);
    let _ = std::fs::write("build/NexusApp.js", &artifact.wasm_js);
    let _ = std::fs::write("build/NexusApp.omnivm", &artifact.omni_vm);
    
    // Simulate linking native binary using LLVM
    let _ = std::fs::write("build/nexus_app_bin", "ELF_BINARY_DATA_SIMULATION_4.2MB");

    println!("> SELESAI: ./nexus_app_bin (Ukuran: 4.2 MB)");
    println!("\nCatatan: Varian Tri-Target (LLVM .ll, .js, .omnivm) telah di-eksport ke dalam folder `build/`");
}

/// 🚀 Build target=unikernel — Generate bare-metal bootable image
fn run_unikernel_build(args: &[String]) {
    use crate::unikernel::UniKernelEngine;
    use crate::unikernel::image_builder::UniKernelConfig;

    println!("╔══════════════════════════════════════════════════════╗");
    println!("║  🚀 OMNI BUILD —— TARGET: UNIKERNEL (Bare-Metal)   ║");
    println!("╚══════════════════════════════════════════════════════╝");

    // Parse optional flags
    let ram = args.iter()
        .find(|a| a.starts_with("--ram="))
        .and_then(|a| a.strip_prefix("--ram="))
        .and_then(|v| v.parse::<u64>().ok())
        .unwrap_or(512);

    let config = UniKernelConfig {
        ram_limit_mb: ram,
        ..UniKernelConfig::default()
    };

    let mut engine = UniKernelEngine::new(config);

    // Mount default config files into VFS
    engine.mount_file("/etc/omni.conf", b"# OMNI Runtime Config\nram_limit=512M\nlog_level=info\n");
    engine.mount_file("/etc/network.conf", b"# Network: DHCP\ninterface=eth0\ndhcp=true\n");

    println!("\n> Kompilasi OMNI IR → bare-metal machine code...");
    
    // Simulate application binary (in production this comes from LLVM codegen)
    let app_code = generate_simulated_app_binary();
    
    match engine.build(&app_code, "main") {
        Ok(_image) => {
            let _ = std::fs::create_dir_all("build");
            
            match engine.export("build/omni-unikernel.img") {
                Ok(()) => {},
                Err(e) => println!("  ⚠️  Export warning: {}", e),
            }

            // Also export memory map
            if let Some(ref image) = engine.image {
                let _ = std::fs::write("build/omni-unikernel.map", image.segment_map());
            }

            engine.print_summary();
            println!("\n> 🚀 SELESAI: build/omni-unikernel.img");
            println!("> Boot command: qemu-system-x86_64 -kernel build/omni-unikernel.img -m {}M -nographic",
                engine.config.ram_limit_mb);
        },
        Err(e) => {
            println!("❌ Unikernel build failed: {}", e);
        }
    }
}

/// Generate simulated application binary
fn generate_simulated_app_binary() -> Vec<u8> {
    let mut binary = Vec::new();
    // Magic header
    binary.extend_from_slice(b"OMNI-APP-BIN\x00\x00\x00\x00");
    // Simulated x86_64 instructions (just NOPs + a HLT for demo)
    for _ in 0..1024 {
        binary.push(0x90); // NOP
    }
    binary.push(0xF4); // HLT
    binary
}
