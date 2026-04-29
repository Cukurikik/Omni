/// OMNI QWEN: Tool Executor
/// Rust threading logic to execute system tools safely when requested by the Qwen LLM agent.
/// Source: QwenLM/Qwen

use std::process::Command;
use std::sync::mpsc;
use std::thread;
use std::time::Duration;

#[derive(Debug)]
pub enum ToolError {
    ExecutionFailed(String),
    Timeout,
    UnauthorizedTool,
}

pub struct ToolRequest {
    pub tool_name: String,
    pub arguments: Vec<String>,
}

pub struct ToolExecutor;

impl ToolExecutor {
    /// Executes a system tool requested by the agent, wrapped in a timeout
    pub fn execute(req: ToolRequest, timeout_secs: u64) -> Result<String, ToolError> {
        // Strict Authorization Mock
        let allowed_tools = vec!["curl", "python3", "ls", "echo"];
        if !allowed_tools.contains(&req.tool_name.as_str()) {
            return Err(ToolError::UnauthorizedTool);
        }

        let (tx, rx) = mpsc::channel();

        thread::spawn(move || {
            let output = Command::new(&req.tool_name)
                .args(&req.arguments)
                .output();
            
            let _ = tx.send(output);
        });

        match rx.recv_timeout(Duration::from_secs(timeout_secs)) {
            Ok(Ok(output)) => {
                if output.status.success() {
                    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
                    Ok(stdout)
                } else {
                    let stderr = String::from_utf8_lossy(&output.stderr).to_string();
                    Err(ToolError::ExecutionFailed(stderr))
                }
            }
            Ok(Err(e)) => Err(ToolError::ExecutionFailed(e.to_string())),
            Err(mpsc::RecvTimeoutError::Timeout) => Err(ToolError::Timeout),
            Err(_) => Err(ToolError::ExecutionFailed("Thread panicked".to_string())),
        }
    }
}
