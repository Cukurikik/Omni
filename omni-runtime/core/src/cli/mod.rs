// pub mod init;
// pub mod fmt;
// pub mod dev;
// pub mod build;
// pub mod test;
// pub mod bootstrap;
// pub mod install;
// pub mod publish;
// pub mod compile;
pub mod get;

// Phase 2: Data Sovereignty & Stress Testing
// pub mod db;
// pub mod profile;
// pub mod vault;
// pub mod tester;

// Phase 3: Global Deployment & Cybersecurity Bare-Metal
// pub mod deployment;
// pub mod orchestration;
// pub mod cybersecurity;
// pub mod distributed;

// Phase 4: Native AI Processing & WebAssembly UI
// pub mod intelligence;
// pub mod interface;
// pub mod multimedia;
// pub mod analytics;

// Phase 6: Absolute Automation & Pipelines
// pub mod meta;
// pub mod cicd;
// pub mod forensics;
// pub mod mesh;

pub fn execute(args: Vec<String>) {
    if args.len() < 2 {
        print_usage();
        return;
    }

    let command = &args[1];

    // Otomatis bikin folder infrastruktur Tahap 3 jika tidak ada (Phase 3 Hook)
    let infra_dirs = [".omni_infra", "jobs", "security"];
    for dir in infra_dirs.iter() {
        if !std::path::Path::new(dir).exists() {
            let _ = std::fs::create_dir_all(dir);
        }
    }

    // Otomatis bikin folder AI & Antarmuka Tahap 4 jika tidak ada (Phase 4 Hook)
    let ai_ui_dirs = ["models", "ui", "shaders"];
    for dir in ai_ui_dirs.iter() {
        if !std::path::Path::new(dir).exists() {
            let _ = std::fs::create_dir_all(dir);
        }
    }

    match command.as_str() {
        "init" => {
            let has_lang = args.iter().find(|a| a.starts_with("--lang="));
            if let Some(lang_flag) = has_lang {
                let lang = lang_flag.split('=').nth(1).unwrap_or("javascript");
                crate::polyglot::execute_real_scaffold(lang, lang);
            } else {
                let project_name = if args.len() > 2 { &args[2] } else { "omni_project" };
                init::run(project_name);
            }
        }
        "worker" => {
            let lang = args.iter().find(|a| a.starts_with("--lang=")).map(|s| s.split('=').nth(1).unwrap()).unwrap_or("go");
            crate::polyglot::execute_real_scaffold("golang", lang);
        }
        "pipeline" => {
            let lang = args.iter().find(|a| a.starts_with("--lang=")).map(|s| s.split('=').nth(1).unwrap()).unwrap_or("cpp");
            crate::polyglot::execute_real_scaffold("cpp", lang);
        }
        "fmt" => {
            fmt::run();
        }
        "dev" => {
            dev::run();
        }
        "build" => {
            build::run(&args[2..]);
        }
        "test-runtime" => {
            test::run_test_suite();
        }
        "bootstrap" => {
            bootstrap::run();
        }
        "install" => {
            install::run();
        }
        "compile" => {
            compile::run(&args[2..]);
        }
        "get" => {
            if args.len() < 3 {
                println!("❌ Missing package name. Usage: omni get <package_name>");
                return;
            }
            get::run(&args[2]);
        }
        // ---- Phase 2 Native Routes ----
        "db" => {
            db::run(&args[2..]);
        }
        "profile" | "trace" | "debug" => {
            profile::run(&args[1..]); // Pass the command itself as well
        }
        "vault" | "env" => {
            vault::run(&args[1..]);
        }
        "test" | "benchmark" => {
            tester::run(&args[1..]);
        }
        // ---- Phase 3 Native Routes ----
        "deploy" | "rollback" | "traffic" | "domain" => {
            deployment::run(&args[2..], command.as_str());
        }
        "unikernel" | "swarm" | "logs" => {
            orchestration::run(&args[2..], command.as_str());
        }
        "shield" | "audit" | "sandbox" | "ddos-mitigate" => {
            cybersecurity::run(&args[2..], command.as_str());
        }
        "job" | "event" | "queue" => {
            distributed::run(&args[2..], command.as_str());
        }
        // ---- Phase 4 Native Routes ----
        "ai" | "hardware" => {
            intelligence::run(&args[2..], command.as_str());
        }
        "ui" => {
            interface::run(&args[2..], command.as_str());
        }
        "media" | "asset" => {
            multimedia::run(&args[2..], command.as_str());
        }
        "report" | "graph" => {
            analytics::run(&args[2..], command.as_str());
        }
        // ---- Phase 6 Native Routes (Absolute Automation) ----
        "auto" => {
            crate::cli::meta::run(&args[2..], command.as_str());
        }
        "release" => {
            crate::cli::cicd::run(&args[2..], command.as_str());
        }
        "forensic" | "heal" | "audit" => {
            crate::cli::forensics::run(&args[2..], command.as_str());
        }
        "mesh" => {
            crate::cli::mesh::run(&args[2..], command.as_str());
        }
        _ => {
            // Check if pipeline is init/run/webhook vs create
            if command == "pipeline" {
                if args.len() > 2 && args[2] == "create" {
                    let lang = args.iter().find(|a| a.starts_with("--lang=")).map(|s| s.split('=').nth(1).unwrap()).unwrap_or("cpp");
                    crate::polyglot::execute_real_scaffold("cpp", lang);
                } else {
                    crate::cli::cicd::run(&args[2..], command.as_str());
                }
            } else {
                println!("❌ Unknown command: {}", command);
                print_usage();
            }
        }
    }
}

fn print_usage() {
    println!("╔══════════════════════════════════════════════════════╗");
    println!("║  ⚙️  OMNI-LANG The Sovereign Arsenal (Phase 8)      ║");
    println!("╚══════════════════════════════════════════════════════╝");
    println!("Usage: omni <command> [args]");
    println!();
    println!("Commands:");
    println!("  init <name>    Create a new Omni project");
    println!("  fmt            Format current project to One True Style");
    println!("  dev            Run local JIT development server with hot-reload");
    println!("  build          Compile to Tri-Target Native/WASM/OMNI-VM binaries");
    println!("    --target=unikernel  Build bare-metal bootable image");
    println!("    --ram=<MB>          Set RAM limit (default: 512)");
    println!("  test-runtime   Run the internal Omni-Core test suite");
    println!("  bootstrap      🐍 Run self-hosting compilation (Oroboros)");
    println!("  get <pkg>      📥 Fetch & add a package to Omnifile from Nexus");
    println!("  install        📦 Install dependencies from Omnifile via Nexus");
    println!("  compile <f>    🔧 Compile .omni source → LLVM IR [--emit-ir] [--emit-ast]");
    println!();
}
