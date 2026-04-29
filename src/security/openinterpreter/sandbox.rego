# OMNI OPEN INTERPRETER: Sandbox Security Policy
# Rego policy enforced by OPA to prevent malicious LLM code generation from running destructive commands.
# Source: OpenInterpreter/open-interpreter

package omni.openinterpreter.sandbox

default allow = false

# Input payload schema:
# {
#   "language": "python" | "bash",
#   "code": "rm -rf /",
#   "user_approved": boolean
# }

# Block lists
dangerous_commands := {"rm -rf /", "mkfs", "dd if=/dev/zero", ":(){ :|:& };:"}
dangerous_imports := {"os.system", "subprocess", "pty"}

# Rule 1: Allow if user explicitly approved AND it doesn't contain known malware signatures
allow {
    input.user_approved == true
    not contains_dangerous_command(input.code)
}

# Rule 2: Bash commands must be checked against the blocklist
contains_dangerous_command(code) {
    input.language == "bash"
    cmd := dangerous_commands[_]
    contains(code, cmd)
}

# Rule 3: Python scripts must not use dangerous standard libraries without approval
contains_dangerous_command(code) {
    input.language == "python"
    imp := dangerous_imports[_]
    contains(code, imp)
}

# Response message for auditing
violation_message = "Code execution blocked: Contains destructive commands or unauthorized imports." {
    not allow
}
