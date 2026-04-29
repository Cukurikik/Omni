// OMNI System Layer: gptcommit_hook.c
// Implements a low-level C hook for Git prepare-commit-msg, interfacing with LLMs.
// Strict bounds: Max 4096 bytes for git diff input, preventing excessive token usage.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_DIFF_SIZE 4096
#define MAX_COMMIT_MSG_SIZE 1024

typedef struct {
    int code;
    const char* message;
} OmniError;

typedef struct {
    char* data;
    OmniError error;
} OmniResult_String;

// External FFI provided by OMNI Rust LLM client
extern OmniResult_String omni_llm_generate_commit(const char* diff_payload, size_t len);

OmniError run_gptcommit_hook(const char* diff_path, const char* msg_path) {
    FILE* diff_file = fopen(diff_path, "r");
    if (!diff_file) {
        return (OmniError){.code = 1, .message = "Failed to open diff file."};
    }

    char diff_buffer[MAX_DIFF_SIZE];
    size_t read_bytes = fread(diff_buffer, 1, MAX_DIFF_SIZE - 1, diff_file);
    diff_buffer[read_bytes] = '\0';
    fclose(diff_file);

    if (read_bytes == MAX_DIFF_SIZE - 1) {
        // Warning: Diff truncated, but we proceed with bounded context
    }

    // Call LLM over FFI
    OmniResult_String llm_result = omni_llm_generate_commit(diff_buffer, read_bytes);
    
    if (llm_result.error.code != 0) {
        return llm_result.error;
    }

    // Write back to commit msg file
    FILE* msg_file = fopen(msg_path, "w");
    if (!msg_file) {
        return (OmniError){.code = 2, .message = "Failed to open commit message file for writing."};
    }

    size_t write_len = strnlen(llm_result.data, MAX_COMMIT_MSG_SIZE);
    fwrite(llm_result.data, 1, write_len, msg_file);
    fclose(msg_file);

    return (OmniError){.code = 0, .message = "Success"};
}

int main(int argc, char** argv) {
    if (argc < 3) {
        fprintf(stderr, "Usage: %s <diff_file> <commit_msg_file>\n", argv[0]);
        return 1;
    }

    OmniError err = run_gptcommit_hook(argv[1], argv[2]);
    if (err.code != 0) {
        fprintf(stderr, "GPTCommit Error: %s\n", err.message);
        return err.code;
    }

    return 0;
}
