pub mod python;
pub mod golang;
pub mod cpp;
pub mod others;

pub fn execute_real_scaffold(command: &str, lang: &str) {
    match command {
        "python" => {
            python::scaffold_and_run();
        }
        "golang" | "go" => {
            golang::scaffold_and_run();
        }
        "cpp" | "c++" | "c" => {
            cpp::scaffold_and_run();
        }
        _ => {
            others::scaffold(lang);
        }
    }
}
