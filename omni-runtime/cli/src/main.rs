use std::env;
use std::process;

mod commands;

fn print_banner() {
    println!("â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”");
    println!("ðŸª ANTIGRAVITY v2.0 â€” OMNI CLI ONLINE");
    println!("âš¡ Runtime   : OMNI-NEXUS / LLVM-Omni");
    println!("ðŸ’¥ Status    : V8 Engine Destructor Active");
    println!("â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”");
}

fn print_help() {
    println!("Usage: omni <COMMAND> [OPTIONS]");
    println!("\nCommands:");
    println!("  run       Run an .omni script via the ultra-fast LLVM engine");
    println!("  build     Compile an OMNI workspace into a zero-latency binary");
    println!("  nexus     Interact with the OMNI Nexus registry (install, publish)");
    println!("  serve     Spin up a 10-million RPS HTTP/3 server natively");
    println!("  check     Analyze code using the OMNI Architect rules
  cloud     Deploy zero-cold-start Unikernels to OMNI PaaS (Monadic Error Enforced)");
    println!("\nRun 'omni help <command>' for more information.");
}

fn main() {
    let args: Vec<String> = env::args().collect();
    
    if args.len() < 2 {
        print_banner();
        print_help();
        process::exit(0);
    }

    let command = args[1].as_str();

    match command {
        "run" => commands::run::execute(&args[2..]),
        "build" => commands::build::execute(&args[2..]),
        "nexus" => commands::nexus::execute(&args[2..]),
        "serve" => commands::serve::execute(&args[2..]),
        "check" => commands::check::execute(&args[2..]),
        "cloud" => commands::cloud::execute(&args[2..]),
        "help" | "--help" | "-h" => {
            print_banner();
            print_help();
        }
        _ => {
            eprintln!("âŒ Fatal: Unknown command '{}'", command);
            eprintln!("Try 'omni help' for maximum guidance.");
            process::exit(1);
        }
    }
}

