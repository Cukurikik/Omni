// OMNI Divine Memory Integration: Inspired by MOSS
// System Layer - C FFI Header connecting Elixir dialogue state to low-level tokenizers

#ifndef OMNI_MOSS_FFI_H
#define OMNI_MOSS_FFI_H

#include <stddef.h>
#include <stdint.h>

#define MOSS_MAX_TOKENS 8192

typedef struct {
    int code;
    const char* message;
} OmniError;

typedef struct {
    int is_ok;
    int32_t* token_array;
    size_t count;
    OmniError error;
} OmniTokenResult;

// Called by Elixir NIFs
OmniTokenResult moss_tokenize_string(const char* input_str);

void moss_free_tokens(int32_t* token_array);

#endif // OMNI_MOSS_FFI_H
