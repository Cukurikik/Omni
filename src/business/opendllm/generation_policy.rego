package opendllm.policy

default is_code_safe = false

is_code_safe {
    not contains(input.code, "eval(")
    not contains(input.code, "exec(")
    not contains(input.code, "os.system(")
}

omni_result = {
    "value": is_code_safe,
    "error": null,
    "is_ok": true
}
