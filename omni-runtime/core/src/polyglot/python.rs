use std::fs;
use std::path::Path;
use std::process::{Command, Stdio};

pub fn scaffold_and_run() {
    let project_dir = Path::new("omni_python_backend");

    if !project_dir.exists() {
        fs::create_dir_all(project_dir).unwrap();
    }

    let main_py = project_dir.join("main.py");
    let req_txt = project_dir.join("requirements.txt");

    // Real FastAPI Template
    let py_code = r#"
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="OMNI-FastAPI Real Engine")

@app.get("/")
def read_root():
    return {"status": "success", "message": "OMNI Python Backend is LIVE!", "engine": "FastAPI"}

@app.get("/ai/status")
def ai_status():
    return {"model": "omni_vision_2.0", "quantized": True, "device": "cuda:0"}

if __name__ == "__main__":
    print("🚀 [OMNI-PYTHON] Menyulut FastAPI di port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
"#;

    let reqs = "fastapi\nuvicorn\n";

    fs::write(&main_py, py_code.trim()).expect("Gagal menulis main.py");
    fs::write(&req_txt, reqs).expect("Gagal menulis requirements.txt");

    println!("✅ [OMNI POLYGLOT] Scaffolding Python (FastAPI) siap di ./omni_python_backend");
    println!("⚙️  Menjalankan installer uvicorn & FastAPI dalam subprocess...");

    // Install dependencies (skip pip install if already installed)
    let _ = Command::new("pip")
        .args(&["install", "-r", "requirements.txt"])
        .current_dir(project_dir)
        .stdout(Stdio::null())
        .status();

    println!("🔥 [OMNI POLYGLOT] Memicu eksekusi Server FastAPI Asli...");

    match Command::new("python")
        .arg("main.py")
        .current_dir(project_dir)
        .spawn() {
            Ok(child) => {
                println!("✅ [PID: {}] Proses Uvicorn Native Berjalan di port 8000!", child.id());
            }
            Err(e) => {
                println!("❌ Gagal menjalankan Python: {}", e);
            }
        }
}
