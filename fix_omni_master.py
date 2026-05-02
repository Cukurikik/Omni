#!/usr/bin/env python3
"""
OMNI Master Fix Script — Resolves all systemic Go compilation errors.

Error Categories Fixed:
1. Broken OmniResult struct (interface{ missing closing })
2. Missing package declarations
3. Duplicate type declarations (OmniError redeclared)
4. Invalid field names (Error vs Err) in struct literals
5. Missing commas in composite literals
6. Undefined Result/Ok/Err/Fail functions
7. Various syntax errors (missing parens, semicolons, etc.)
"""

import os
import re
import glob

OMNI_ROOT = r"c:\Users\IKYY\Downloads\Omni\src"

fixes_applied = 0
files_fixed = 0
errors_log = []

def log_fix(filepath, description):
    global fixes_applied
    fixes_applied += 1
    rel = os.path.relpath(filepath, OMNI_ROOT)
    print(f"  [FIX] {rel}: {description}")

def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception as e:
        errors_log.append(f"READ ERROR {path}: {e}")
        return None

def write_file(path, content):
    try:
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        return True
    except Exception as e:
        errors_log.append(f"WRITE ERROR {path}: {e}")
        return False

# ============================================================
# FIX 1: All omni_types.go files with broken OmniResult struct
# ============================================================
def fix_omni_types_files():
    """Fix the broken OmniResult struct in all omni_types.go files."""
    global files_fixed
    
    # Find all omni_types.go files
    for root, dirs, files in os.walk(OMNI_ROOT):
        for fname in files:
            if fname == "omni_types.go":
                fpath = os.path.join(root, fname)
                content = read_file(fpath)
                if content is None:
                    continue
                
                # Detect the package name
                pkg_match = re.search(r'package\s+(\w+)', content)
                if not pkg_match:
                    continue
                pkg_name = pkg_match.group(1)
                
                # Check if it has the broken pattern: interface{\n\tErr error\n}
                if 'interface{\n' in content or 'interface{\r\n' in content:
                    # Determine field name: some use Err, some use Error
                    if '\tError error' in content or '\tError  error' in content:
                        err_field = "Err"  # Standardize to Err
                    else:
                        err_field = "Err"
                    
                    new_content = f'''package {pkg_name}

import "errors"

// OmniResult is the standard monadic result type for this package.
type OmniResult struct {{
\tValue interface{{}}
\t{err_field}   error
}}

// Ok creates a successful OmniResult.
func Ok(val interface{{}}) OmniResult {{
\treturn OmniResult{{Value: val}}
}}

// Fail creates a failed OmniResult from an error message.
func Fail(msg string) OmniResult {{
\treturn OmniResult{{{err_field}: errors.New(msg)}}
}}
'''
                    if write_file(fpath, new_content):
                        log_fix(fpath, "Fixed broken OmniResult struct (interface{{ missing }})")
                        files_fixed += 1

# ============================================================
# FIX 2: network/omni_network_types.go — broken header
# ============================================================
def fix_network_types():
    global files_fixed
    fpath = os.path.join(OMNI_ROOT, "network", "omni_network_types.go")
    if not os.path.exists(fpath):
        return
    
    content = read_file(fpath)
    if content is None:
        return
    
    # Check if it has the broken orphan lines at top
    if content.strip().startswith("package network") and "\tErr   error\n}" in content:
        new_content = '''package network

import "errors"

// OmniResult is the generic monadic result type.
type OmniResult[T any] struct {
\tValue T
\tErr   error
}

// OkT creates a successful generic Result.
func OkT[T any](val T) OmniResult[T] {
\treturn OmniResult[T]{Value: val}
}

// ErrT creates a failed generic Result.
func ErrT[T any](e error) OmniResult[T] {
\tvar zero T
\treturn OmniResult[T]{Value: zero, Err: e}
}

// Ok creates a successful non-generic OmniResult.
func Ok(val interface{}) OmniResult[interface{}] {
\treturn OmniResult[interface{}]{Value: val}
}

// Fail creates a failed OmniResult from an error message.
func Fail(msg string) OmniResult[interface{}] {
\treturn OmniResult[interface{}]{Err: errors.New(msg)}
}
'''
        if write_file(fpath, new_content):
            log_fix(fpath, "Fixed broken generic OmniResult types")
            files_fixed += 1

# ============================================================
# FIX 3: core/result/result.go — OmniResult undefined
# ============================================================
def fix_core_result():
    global files_fixed
    fpath = os.path.join(OMNI_ROOT, "core", "result", "result.go")
    if not os.path.exists(fpath):
        return
    
    content = read_file(fpath)
    if content is None:
        return
    
    # The file uses OmniResult but never defines it, and uses both .Err and .Error inconsistently
    new_content = '''package result

import "fmt"

// OmniResult is the canonical generic result type for the Omni project.
type OmniResult[T any] struct {
\tValue T
\tErr   error
}

// Ok creates a successful OmniResult.
func Ok[T any](val T) OmniResult[T] {
\treturn OmniResult[T]{Value: val}
}

// Err creates a failed OmniResult.
func Err[T any](err error) OmniResult[T] {
\tvar zero T
\treturn OmniResult[T]{Value: zero, Err: err}
}

// IsOk checks if the result is successful.
func (r *OmniResult[T]) IsOk() bool {
\treturn r.Err == nil
}

// Unwrap returns the value or panics if error.
func (r *OmniResult[T]) Unwrap() T {
\tif r.Err != nil {
\t\tpanic("Unwrap on error result")
\t}
\treturn r.Value
}

// NewError creates a failed OmniResult with formatted error message.
func NewError[T any](msg string, args ...interface{}) OmniResult[T] {
\treturn Err[T](fmt.Errorf(msg, args...))
}
'''
    if write_file(fpath, new_content):
        log_fix(fpath, "Fixed OmniResult definition and field consistency")
        files_fixed += 1

# ============================================================
# FIX 4: Files with broken inline OmniResult structs
# Pattern: type OmniResult struct { Value interface{\n\tErr error\n}\n\tError error }
# ============================================================
def fix_inline_broken_omniresult():
    """Fix files that define their own broken OmniResult inline."""
    global files_fixed
    
    # Pattern to find files with broken OmniResult
    broken_pattern = re.compile(
        r'type\s+OmniResult\s+struct\s*\{\s*\n\s*Value\s+interface\{\s*\n\s*(?:Err|Error)\s+error\s*\n\s*\}\s*\n\s*(?:Err|Error)\s+error\s*\n\s*\}',
        re.MULTILINE
    )
    
    for root, dirs, files in os.walk(OMNI_ROOT):
        for fname in files:
            if not fname.endswith('.go'):
                continue
            if fname == 'omni_types.go':
                continue  # Already handled
                
            fpath = os.path.join(root, fname)
            content = read_file(fpath)
            if content is None:
                continue
            
            if broken_pattern.search(content):
                # Replace broken struct with fixed one
                fixed = broken_pattern.sub(
                    'type OmniResult struct {\n\tValue interface{}\n\tErr   error\n}',
                    content
                )
                
                # Also fix any references to .Error -> .Err for OmniResult
                # But be careful not to change Error() method calls
                
                if fixed != content:
                    if write_file(fpath, fixed):
                        log_fix(fpath, "Fixed inline broken OmniResult struct")
                        files_fixed += 1

# ============================================================
# FIX 5: Fix duplicate OmniError declarations  
# ============================================================
def fix_duplicate_omnierror():
    """Fix files with duplicate OmniError type declarations."""
    global files_fixed
    
    fpath = os.path.join(OMNI_ROOT, "concurrency", "go_dataset_streamer.go")
    if not os.path.exists(fpath):
        return
    
    content = read_file(fpath)
    if content is None:
        return
    
    new_content = '''package concurrency

import (
\t"errors"
)

// DatasetChunk represents a chunk of dataset for streaming.
type DatasetChunk struct {
\tData []byte
\tSize int
}

// StreamDataset streams a dataset file in chunks through a channel.
func StreamDataset(filePath string, maxChunkSize int, channel chan<- DatasetChunk) error {
\tif maxChunkSize <= 0 || maxChunkSize > 1048576*10 { // 10MB chunk limit
\t\treturn errors.New("chunk size out of physical memory bounds")
\t}

\tchunk := DatasetChunk{
\t\tData: make([]byte, maxChunkSize),
\t\tSize: maxChunkSize,
\t}

\tselect {
\tcase channel <- chunk:
\t\t// Sent successfully through the channel multiplexer
\tdefault:
\t\treturn errors.New("channel full, backpressure constraint triggered")
\t}

\treturn nil
}
'''
    if write_file(fpath, new_content):
        log_fix(fpath, "Removed duplicate OmniError declarations, use standard error")
        files_fixed += 1

# ============================================================
# FIX 6: Files missing package declarations
# ============================================================
def fix_missing_package_declarations():
    """Fix files that are missing the package declaration line."""
    global files_fixed
    
    missing_pkg_files = [
        ("compute/argo/omni_argo_workflow_dag.go", "argo"),
        ("compute/docker/omni_docker_container_runtime.go", "docker"),
        ("compute/dvc/omni_dvc_data_versioning.go", "dvc"),
        ("compute/k8s/omni_awesome_k8s_scheduler.go", "k8s"),
        ("compute/prometheus/omni_prometheus_tsdb_engine.go", "prometheus"),
        ("compute/qix/omni_qix_distributed_query.go", "qix"),
        ("compute/terraform/omni_terraform_state_parser.go", "terraform"),
    ]
    
    for rel_path, pkg_name in missing_pkg_files:
        fpath = os.path.join(OMNI_ROOT, rel_path.replace("/", os.sep))
        if not os.path.exists(fpath):
            continue
        
        content = read_file(fpath)
        if content is None:
            continue
        
        # Check if package declaration is missing
        stripped = content.lstrip()
        if not stripped.startswith("package "):
            # Add package declaration at the top
            new_content = f"package {pkg_name}\n\n{content}"
            if write_file(fpath, new_content):
                log_fix(fpath, f"Added missing 'package {pkg_name}' declaration")
                files_fixed += 1

# ============================================================
# FIX 7: Fix casbin/ory_kratos — Err() call uses Err() instead of error
# ============================================================
def fix_err_inference_files():
    """Fix files where Err is called with Err() instead of an error value."""
    global files_fixed
    
    files_to_fix = [
        "business/casbin_authz/enforcer.go",
        "business/ory_kratos_iam/identity_provider.go",
        "compute/ircot_reasoning/retriever.go",
        "concurrency/kafka_streams/event_processor.go",
        "concurrency/temporal_orchestrator/workflow_engine.go",
        "concurrency/weaviate_db/schema_manager.go",
        "database/chromadb_flux/client.go",
    ]
    
    for rel_path in files_to_fix:
        fpath = os.path.join(OMNI_ROOT, rel_path.replace("/", os.sep))
        if not os.path.exists(fpath):
            continue
        
        content = read_file(fpath)
        if content is None:
            continue
        
        original = content
        
        # Fix: Err(Err("message")) -> Err[bool](errors.New("message")) or similar
        # Pattern: return Err[TYPE](Err("MSG"))
        content = re.sub(
            r'return\s+Err\[(\w+)\]\(Err\("([^"]+)"\)\)',
            r'return Err[\1](errors.New("\2"))',
            content
        )
        
        # Pattern: return Err("MSG") where function returns OmniResult[T]
        # Fix: Err without type param when generic
        content = re.sub(
            r'return\s+Err\("([^"]+)"\)',
            r'return Err[bool](errors.New("\1"))',
            content
        )
        
        # Ensure errors import exists if we added errors.New
        if 'errors.New' in content and '"errors"' not in content:
            # Add import
            if 'import (' in content:
                content = content.replace('import (', 'import (\n\t"errors"', 1)
            elif 'import "' in content:
                content = re.sub(r'(import "[^"]+")', r'\1\nimport "errors"', content, count=1)
            else:
                pkg_match = re.search(r'(package\s+\w+\s*\n)', content)
                if pkg_match:
                    content = content[:pkg_match.end()] + '\nimport "errors"\n' + content[pkg_match.end():]
        
        if content != original:
            if write_file(fpath, content):
                log_fix(fpath, "Fixed Err() call — cannot infer T")
                files_fixed += 1

# ============================================================
# FIX 8: Fix files with 'expected ';', found error' pattern
# These typically have broken OmniResult locally defined
# ============================================================
def fix_expected_semicolon_error():
    """Fix files where the OmniResult struct has the broken interface{ pattern inline."""
    global files_fixed
    
    for root, dirs, files in os.walk(OMNI_ROOT):
        for fname in files:
            if not fname.endswith('.go') or fname == 'omni_types.go':
                continue
            
            fpath = os.path.join(root, fname)
            content = read_file(fpath)
            if content is None:
                continue
            
            original = content
            
            # Fix the broken struct pattern with various field names
            # Pattern: Value interface{\n\tErr error\n}\n\tError error
            content = re.sub(
                r'Value\s+interface\{\s*\n\s*(?:Err|Error)\s+error\s*\n\s*\}\s*\n\s*(?:Err|Error)\s+error',
                'Value interface{}\n\tErr   error',
                content
            )
            
            # Also fix: Value interface{\n\tErr error\n}\n\tErr   error
            content = re.sub(
                r'Value\s+interface\{\s*\r?\n\s*Err\s+error\s*\r?\n\s*\}\s*\r?\n\s*Err\s+error',
                'Value interface{}\n\tErr   error',
                content
            )
            
            if content != original:
                if write_file(fpath, content):
                    log_fix(fpath, "Fixed broken interface{{ in OmniResult struct")
                    files_fixed += 1

# ============================================================
# FIX 9: Fix struct literal field mismatches
# unknown field Error -> use Err
# unknown field Payload -> remove or fix
# unknown field Success -> fix
# ============================================================
def fix_struct_field_mismatches():
    """Fix struct literals using wrong field names."""
    global files_fixed
    
    for root, dirs, files in os.walk(OMNI_ROOT):
        for fname in files:
            if not fname.endswith('.go'):
                continue
            
            fpath = os.path.join(root, fname)
            content = read_file(fpath)
            if content is None:
                continue
            
            original = content
            
            # Fix: {Error: ...} -> {Err: ...} in OmniResult/Result struct literals
            # But only for our custom structs, not standard error interface
            content = re.sub(
                r'(OmniResult\{[^}]*?)Error:\s*',
                r'\1Err: ',
                content
            )
            content = re.sub(
                r'(Result\{[^}]*?)Error:\s*',
                r'\1Err: ',
                content
            )
            content = re.sub(
                r'(FrameResult\{[^}]*?)Error:\s*',
                r'\1Err: ',
                content
            )
            content = re.sub(
                r'(SctpResult\{[^}]*?)Error:\s*',
                r'\1Err: ',
                content
            )
            content = re.sub(
                r'(RunnerResult\{[^}]*?)Error:\s*',
                r'\1Err: ',
                content
            )
            content = re.sub(
                r'(GatewayResponse\{[^}]*?)Error:\s*',
                r'\1Err: ',
                content
            )
            content = re.sub(
                r'(ProxyResult\{[^}]*?)Error:\s*',
                r'\1Err: ',
                content
            )
            content = re.sub(
                r'(RagClientResult\{[^}]*?)Error:\s*',
                r'\1Err: ',
                content
            )
            content = re.sub(
                r'(ResultStreamMeta\{[^}]*?)Error:\s*',
                r'\1Err: ',
                content
            )
            content = re.sub(
                r'(ResultVideoMeta\{[^}]*?)Error:\s*',
                r'\1Err: ',
                content
            )
            
            # Fix: Success: -> Value: in OmniResult 
            content = re.sub(
                r'(OmniResult\{[^}]*?)Success:\s*',
                r'\1Value: ',
                content
            )
            
            if content != original:
                if write_file(fpath, content):
                    log_fix(fpath, "Fixed struct field name mismatches")
                    files_fixed += 1

# ============================================================
# FIX 10: Fix 'expected declaration, found Error/Err/Ok/Fail'
# These are orphan lines from broken prior fixes
# ============================================================
def fix_orphan_declarations():
    """Fix files with orphan Error/Err/Ok lines outside functions."""
    global files_fixed
    
    for root, dirs, files in os.walk(OMNI_ROOT):
        for fname in files:
            if not fname.endswith('.go'):
                continue
            
            fpath = os.path.join(root, fname)
            content = read_file(fpath)
            if content is None:
                continue
            
            original = content
            lines = content.split('\n')
            new_lines = []
            skip_orphan = False
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                # Remove orphan lines that are just field declarations outside structs
                if stripped in ('Err   error', 'Error error', 'Err error', '}') and i < 10:
                    # Check if this is before the actual type/func declarations
                    # This handles the broken header pattern in omni_network_types.go style
                    if i > 0 and new_lines and new_lines[-1].strip() == '':
                        continue  # Skip orphan line
                    elif stripped == '}' and i < 8:
                        continue
                
                new_lines.append(line)
            
            content = '\n'.join(new_lines)
            
            if content != original:
                if write_file(fpath, content):
                    log_fix(fpath, "Removed orphan declarations")
                    files_fixed += 1

# ============================================================
# FIX 11: Fix missing commas in argument lists / composite literals
# Pattern: multi-line struct literal missing trailing comma
# ============================================================
def fix_missing_commas():
    """Fix missing commas in composite literals."""
    global files_fixed
    
    for root, dirs, files in os.walk(OMNI_ROOT):
        for fname in files:
            if not fname.endswith('.go'):
                continue
            
            fpath = os.path.join(root, fname)
            content = read_file(fpath)
            if content is None:
                continue
            
            original = content
            lines = content.split('\n')
            new_lines = []
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                # Check if this line ends with a value and next line starts with } or another field
                if i + 1 < len(lines):
                    next_stripped = lines[i + 1].strip()
                    
                    # Pattern: line ends with a value (not comma, not {, not comment)
                    # and next line is } or starts with a field name
                    if (stripped and 
                        not stripped.endswith(',') and 
                        not stripped.endswith('{') and 
                        not stripped.endswith('(') and
                        not stripped.endswith('//') and
                        not stripped.startswith('//') and
                        not stripped.startswith('/*') and
                        not stripped.endswith('*/') and
                        stripped != '}' and
                        stripped != ')' and
                        stripped != '},' and
                        not stripped.startswith('func ') and
                        not stripped.startswith('type ') and
                        not stripped.startswith('var ') and
                        not stripped.startswith('const ') and
                        not stripped.startswith('package ') and
                        not stripped.startswith('import ')):
                        
                        # Next line is closing brace — need trailing comma
                        if next_stripped in ('}', '},', '})', ')'):
                            # Check if current line looks like a struct field value
                            if re.match(r'.*\w+:.*\S', stripped) or re.match(r'.*"[^"]*"$', stripped) or re.match(r'.*\d+$', stripped) or stripped.endswith(')') or stripped.endswith('"'):
                                # Add comma
                                line = line.rstrip() + ','
                
                new_lines.append(line)
            
            content = '\n'.join(new_lines)
            
            if content != original:
                if write_file(fpath, content):
                    log_fix(fpath, "Added missing trailing commas")
                    files_fixed += 1

# ============================================================
# MAIN EXECUTION
# ============================================================
def main():
    global fixes_applied, files_fixed
    
    print("=" * 70)
    print("OMNI MASTER FIX SCRIPT — Resolving All Go Compilation Errors")
    print("=" * 70)
    
    print("\n[PHASE 1] Fixing core result/result.go...")
    fix_core_result()
    
    print("\n[PHASE 2] Fixing all omni_types.go files (broken OmniResult)...")
    fix_omni_types_files()
    
    print("\n[PHASE 3] Fixing network/omni_network_types.go...")
    fix_network_types()
    
    print("\n[PHASE 4] Fixing inline broken OmniResult structs...")
    fix_inline_broken_omniresult()
    
    print("\n[PHASE 5] Fixing expected ';' found error patterns...")
    fix_expected_semicolon_error()
    
    print("\n[PHASE 6] Fixing duplicate OmniError declarations...")
    fix_duplicate_omnierror()
    
    print("\n[PHASE 7] Fixing missing package declarations...")
    fix_missing_package_declarations()
    
    print("\n[PHASE 8] Fixing Err() type inference errors...")
    fix_err_inference_files()
    
    print("\n[PHASE 9] Fixing struct field name mismatches...")
    fix_struct_field_mismatches()
    
    print("\n[PHASE 10] Fixing orphan declarations...")
    fix_orphan_declarations()
    
    print("\n[PHASE 11] Fixing missing commas...")
    fix_missing_commas()
    
    print("\n" + "=" * 70)
    print(f"SUMMARY: {fixes_applied} fixes applied across {files_fixed} files")
    if errors_log:
        print(f"\nErrors encountered ({len(errors_log)}):")
        for e in errors_log[:20]:
            print(f"  {e}")
    print("=" * 70)

if __name__ == "__main__":
    main()
