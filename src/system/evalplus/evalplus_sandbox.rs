// EvalPlus Code Execution Sandbox
// Enforces strict cgroups and memory limits for evaluating generated code.

pub struct OmniResult<T, E> {
    pub value: Option<T>,
    pub error: Option<E>,
}

pub struct SandboxConfig {
    pub max_memory_mb: u32,
    pub max_cpu_time_ms: u32,
    pub allow_network: bool,
}

pub struct SandboxExecution {
    pid: u32,
    cgroup_path: String,
}

impl SandboxExecution {
    pub fn new(code: &str, config: SandboxConfig) -> OmniResult<Self, String> {
        if code.len() > 1024 * 1024 {
            return OmniResult { value: None, error: Some("Code payload exceeds 1MB bound".to_string()) };
        }

        let pid = unsafe { create_isolated_process() };
        if pid == 0 {
             return OmniResult { value: None, error: Some("Process fork failed".to_string()) };
        }

        let cgroup_path = format!("/sys/fs/cgroup/evalplus_{}", pid);
        unsafe {
            apply_cgroup_limits(&cgroup_path, config.max_memory_mb, config.max_cpu_time_ms);
        }

        OmniResult {
            value: Some(Self { pid, cgroup_path }),
            error: None,
        }
    }

    pub fn terminate(&self) -> OmniResult<(), String> {
        unsafe { kill_process(self.pid) };
        OmniResult { value: Some(()), error: None }
    }
}

extern "C" {
    fn create_isolated_process() -> u32;
    fn apply_cgroup_limits(path: &str, mem: u32, cpu: u32);
    fn kill_process(pid: u32);
}
