package omni.agent.autogpt

# OMNI AUTOGPT: Agent Tool Sandbox Boundaries
# Validates whether an autonomous agent is allowed to execute a requested shell command or file system action.
# Source: Significant-Gravitas/AutoGPT

default action_allowed = false

# Allow HTTP GET requests to safe domains
action_allowed {
    input.tool == "web_request"
    input.method == "GET"
    not is_blacklisted_domain(input.target_url)
}

# Allow file read/write ONLY in the workspace directory
action_allowed {
    input.tool == "file_system"
    input.operation in {"read", "write"}
    startswith(input.path, "/workspace/")
    not contains(input.path, "..")
}

# Strictly Deny Dangerous Shell Commands
deny[msg] {
    input.tool == "shell_execute"
    dangerous_command(input.command)
    msg := sprintf("Command blocked: Agent attempted dangerous operation '%v'", [input.command])
}

dangerous_command(cmd) {
    dangerous_keywords := {"rm -rf", "mkfs", "dd ", "chmod 777", "> /dev/sda"}
    contains(cmd, dangerous_keywords[_])
}

is_blacklisted_domain(url) {
    blacklisted := {"localhost", "127.0.0.1", "169.254.169.254", "internal-api.omni"}
    contains(url, blacklisted[_])
}
