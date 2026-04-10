
use omnicore::singularity::v8_micro_isolate::V8MicroIsolate;

fn main() {
    let payload = include_str!("../payload.js");
    let mut micro_v8 = V8MicroIsolate::new();
    
    // Inisialisasi V8
    if let Err(e) = micro_v8.initialize() {
        eprintln!("❌ Native Engine Error: {}", e);
        return;
    }
    
    // Eksekusi Payload Tertanam
    match micro_v8.execute(payload) {
        Ok(output) => {
            if !output.is_empty() && output != "\"\"" {
                println!("{}", output.trim_matches('"').replace("\\n", "\n"));
            }
        }
        Err(e) => {
            eprintln!("❌ Omni Runtime Error: {}", e);
            std::process::exit(1);
        }
    }
}
