/* OMNI System Layer
 * MRI (CRuby) VM Embedding Bridge
 * Based on ruby/ruby. Embeds the standard Ruby interpreter inside the Omni Engine.
 */

#include <stdio.h>
#include <stdlib.h>

// Simulating ruby.h
#define VALUE unsigned long
VALUE rb_eval_string(const char *str) { return 1; }
void ruby_init(void) {}
void ruby_init_loadpath(void) {}
void ruby_script(const char* name) {}
int ruby_cleanup(int state) { return 0; }

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    int is_initialized;
} OmniRubyEnvironment;

/* Bootstraps the CRuby VM inside the C-ABI memory space */
OmniRubyEnvironment* omni_ruby_vm_init() {
    printf("OMNI C: Bootstrapping Embedded MRI (CRuby) VM.\n");
    
    OmniRubyEnvironment* env = (OmniRubyEnvironment*)malloc(sizeof(OmniRubyEnvironment));
    
    // Standard Ruby initialization sequence
    ruby_init();
    ruby_init_loadpath();
    ruby_script("omni_embedded_ruby");
    
    env->is_initialized = 1;
    printf("OMNI C: Embedded Ruby VM ready.\n");
    return env;
}

/* Executes arbitrary Ruby code */
int32_t omni_ruby_eval(OmniRubyEnvironment* env, const char* ruby_code) {
    if (!env || !env->is_initialized) return -1;
    
    printf("OMNI C: Evaluating Ruby code in VM...\n");
    
    // In production, use rb_eval_string_protect to catch Ruby exceptions cleanly
    // int state;
    // VALUE result = rb_eval_string_protect(ruby_code, &state);
    
    VALUE result = rb_eval_string(ruby_code);
    
    if (result) {
        printf("OMNI C: Ruby evaluation successful.\n");
        return 0; // Success
    }
    
    return -2; // Evaluation error
}

void omni_ruby_vm_shutdown(OmniRubyEnvironment* env) {
    if (env && env->is_initialized) {
        ruby_cleanup(0);
        free(env);
        printf("OMNI C: Embedded Ruby VM shutdown.\n");
    }
}

#ifdef __cplusplus
}
#endif
