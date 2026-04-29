#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libpostal/libpostal.h>

// OMNI C System Layer: Libpostal FFI Bridge
// High-speed deterministic address normalization using statistical NLP.

typedef struct {
    char** expansions;
    size_t count;
    char* error_msg;
} PostalResult;

PostalResult omni_normalize_address(const char* address) {
    PostalResult result = {NULL, 0, NULL};

    if (!libpostal_setup() || !libpostal_setup_language_classifier()) {
        result.error_msg = strdup("Failed to initialize libpostal setup.");
        return result;
    }

    libpostal_normalize_options_t options = libpostal_get_default_options();
    options.address_components = LIBPOSTAL_ADDRESS_ANY | LIBPOSTAL_ADDRESS_NAME | LIBPOSTAL_ADDRESS_STREET;
    
    size_t num_expansions = 0;
    char **expansions = libpostal_expand_address(address, options, &num_expansions);

    if (num_expansions == 0) {
        result.error_msg = strdup("No expansions found or parsing failed.");
        return result;
    }

    result.expansions = (char**)malloc(num_expansions * sizeof(char*));
    for (size_t i = 0; i < num_expansions; i++) {
        result.expansions[i] = strdup(expansions[i]);
    }
    result.count = num_expansions;

    // Free libpostal structures
    libpostal_expansion_array_destroy(expansions, num_expansions);
    libpostal_teardown();
    libpostal_teardown_language_classifier();

    return result;
}

void omni_free_postal_result(PostalResult* result) {
    if (result->expansions != NULL) {
        for (size_t i = 0; i < result->count; i++) {
            free(result->expansions[i]);
        }
        free(result->expansions);
    }
    if (result->error_msg != NULL) {
        free(result->error_msg);
    }
}
