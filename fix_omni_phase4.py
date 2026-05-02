#!/usr/bin/env python3
"""
OMNI Phase 4 — Fix remaining structural issues:
1. Duplicate package declarations
2. Orphan incomplete OmniResult structs
3. Missing closing braces in functions
4. Commas after struct field tags
5. Commas after interface methods
6. Commas after const values in const blocks
"""

import os
import re

OMNI_ROOT = r"c:\Users\IKYY\Downloads\Omni\src"
fixes_applied = 0
files_fixed = 0

def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except:
        return None

def write_file(path, content):
    try:
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        return True
    except:
        return False

def fix_json_tag_commas():
    """Remove trailing commas from struct fields with json tags."""
    global files_fixed, fixes_applied
    
    for root, dirs, files in os.walk(OMNI_ROOT):
        for fname in files:
            if not fname.endswith('.go'):
                continue
            fpath = os.path.join(root, fname)
            content = read_file(fpath)
            if content is None:
                continue
            original = content
            
            # Fix: `json:"field"`,  -> `json:"field"`
            content = re.sub(r'(`[^`]+`)\s*,\s*$', r'\1', content, flags=re.MULTILINE)
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def fix_const_commas():
    """Remove trailing commas from const values in const blocks."""
    global files_fixed, fixes_applied
    
    for root, dirs, files in os.walk(OMNI_ROOT):
        for fname in files:
            if not fname.endswith('.go'):
                continue
            fpath = os.path.join(root, fname)
            content = read_file(fpath)
            if content is None:
                continue
            original = content
            
            # Fix const block entries with trailing comma
            # StatusComplete JobStatus = "COMPLETE",  -> StatusComplete JobStatus = "COMPLETE"
            content = re.sub(
                r'^(\s*\w+\s+\w+\s*=\s*"[^"]*"),\s*$',
                r'\1',
                content, flags=re.MULTILINE
            )
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def fix_interface_method_commas():
    """Remove trailing commas from interface method declarations."""
    global files_fixed, fixes_applied
    
    for root, dirs, files in os.walk(OMNI_ROOT):
        for fname in files:
            if not fname.endswith('.go'):
                continue
            fpath = os.path.join(root, fname)
            content = read_file(fpath)
            if content is None:
                continue
            original = content
            
            # Fix: MethodName(args) (returns),  -> MethodName(args) (returns)
            # Inside interface blocks
            content = re.sub(
                r'^(\s+\w+\([^)]*\)\s+\([^)]+\))\s*,\s*$',
                r'\1',
                content, flags=re.MULTILINE
            )
            content = re.sub(
                r'^(\s+\w+\([^)]*\)\s+\w+)\s*,\s*$',
                r'\1',
                content, flags=re.MULTILINE
            )
            content = re.sub(
                r'^(\s+\w+\([^)]*\)\s+error)\s*,\s*$',
                r'\1',
                content, flags=re.MULTILINE
            )
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def fix_duplicate_package_decls():
    """Remove duplicate package declarations."""
    global files_fixed, fixes_applied
    
    for root, dirs, files in os.walk(OMNI_ROOT):
        for fname in files:
            if not fname.endswith('.go'):
                continue
            fpath = os.path.join(root, fname)
            content = read_file(fpath)
            if content is None:
                continue
            original = content
            
            # Find all package declarations
            pkg_matches = list(re.finditer(r'^package\s+\w+\s*$', content, re.MULTILINE))
            if len(pkg_matches) > 1:
                # Keep the first one, remove subsequent ones
                # But we need to remove the second occurrence and any orphan import blocks
                for match in pkg_matches[1:]:
                    start = match.start()
                    # Find the next import block or type declaration
                    # Remove the duplicate package line
                    content = content[:start] + content[match.end():]
                
                # Also remove empty import blocks: import (\n    )
                content = re.sub(r'import\s*\(\s*\)\s*\n?', '', content)
                
                if content != original:
                    if write_file(fpath, content):
                        fixes_applied += 1
                        files_fixed += 1

def fix_orphan_omniresult():
    """Fix incomplete OmniResult struct (missing closing brace) followed by a complete one."""
    global files_fixed, fixes_applied
    
    for root, dirs, files in os.walk(OMNI_ROOT):
        for fname in files:
            if not fname.endswith('.go'):
                continue
            fpath = os.path.join(root, fname)
            content = read_file(fpath)
            if content is None:
                continue
            original = content
            
            # Pattern: type OmniResult struct {\n\tValue interface{}\n\ntype OmniResult[T any]
            # The first OmniResult is incomplete (no closing })
            content = re.sub(
                r'type OmniResult struct \{\s*\n\s*Value interface\{\}\s*\n\s*\ntype OmniResult',
                'type OmniResult',
                content
            )
            
            # Also fix: type OmniResult struct {\n\tValue interface{}\n\tErr error\n\ntype OmniResult
            # with missing closing }
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def fix_missing_closing_braces():
    """Fix functions/blocks missing their closing brace."""
    global files_fixed, fixes_applied
    
    for root, dirs, files in os.walk(OMNI_ROOT):
        for fname in files:
            if not fname.endswith('.go'):
                continue
            fpath = os.path.join(root, fname)
            content = read_file(fpath)
            if content is None:
                continue
            original = content
            
            # Pattern: return &Something{\n\t\tfield: value,\n\t}\n\n// Comment or func
            # Missing closing } between } and next func/comment
            # Fix: Add } after the closing of the return struct
            
            # Pattern: return &Struct{...}\n\n(func|//)  -- missing }
            content = re.sub(
                r'(\treturn\s+&\w+\{[^}]*\}\s*\n)\n(// |func )',
                r'\1}\n\n\2',
                content
            )
            
            # More generic: Look for func that opens { but the next func starts before closing
            # This is complex — let's handle specific patterns
            
            # Pattern specifically for constructs like:
            # func Name() *Type {\n\treturn &Type{\n\t\t...\n\t}\n\nfunc  (missing closing })
            lines = content.split('\n')
            fixed_lines = []
            i = 0
            while i < len(lines):
                line = lines[i]
                stripped = line.strip()
                
                # Check if this is a closing } followed by empty line then func/comment
                # But the function above hasn't been closed
                if (stripped == '}' and 
                    i + 1 < len(lines) and 
                    lines[i+1].strip() == '' and
                    i + 2 < len(lines)):
                    
                    next_content = lines[i+2].strip()
                    # Check if next non-empty line is a method/func that shouldn't be inside current scope
                    if (next_content.startswith('// ') or next_content.startswith('func ')):
                        # Count braces to see if we're unbalanced
                        # Look backwards to find the opening func
                        brace_count = 0
                        for j in range(i, -1, -1):
                            brace_count += lines[j].count('}') - lines[j].count('{')
                            if lines[j].strip().startswith('func ') and '{' in lines[j]:
                                break
                        
                        if brace_count < 0:
                            # We're still inside a function, need another }
                            fixed_lines.append(line)
                            fixed_lines.append('}')
                            i += 1
                            continue
                
                fixed_lines.append(line)
                i += 1
            
            content = '\n'.join(fixed_lines)
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def fix_printf_commas():
    """Remove trailing commas from Printf/Sprintf/Println statements."""
    global files_fixed, fixes_applied
    
    for root, dirs, files in os.walk(OMNI_ROOT):
        for fname in files:
            if not fname.endswith('.go'):
                continue
            fpath = os.path.join(root, fname)
            content = read_file(fpath)
            if content is None:
                continue
            original = content
            
            # Fix: fmt.Printf(...),  -> fmt.Printf(...)
            content = re.sub(r'(fmt\.\w+f?\([^)]+\)),\s*$', r'\1', content, flags=re.MULTILINE)
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def fix_string_as_error():
    """Fix cases where a plain string is used as error value."""
    global files_fixed, fixes_applied
    
    for root, dirs, files in os.walk(OMNI_ROOT):
        for fname in files:
            if not fname.endswith('.go'):
                continue
            fpath = os.path.join(root, fname)
            content = read_file(fpath)
            if content is None:
                continue
            original = content
            
            # Fix: Err: "some string"  -> Err: errors.New("some string")
            # In struct literals where error is expected
            content = re.sub(
                r'Err:\s*"([^"]+)"',
                r'Err: errors.New("\1")',
                content
            )
            
            # Ensure errors import
            if 'errors.New' in content and '"errors"' not in content:
                if 'import (' in content:
                    content = content.replace('import (', 'import (\n\t"errors"', 1)
                else:
                    pkg_match = re.search(r'(package\s+\w+\s*\n)', content)
                    if pkg_match:
                        content = content[:pkg_match.end()] + '\nimport "errors"\n' + content[pkg_match.end():]
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def main():
    print("=" * 70)
    print("OMNI PHASE 4 — Structural Fixes")
    print("=" * 70)
    
    print("\n[1] Fixing json tag commas...")
    fix_json_tag_commas()
    
    print("[2] Fixing const block commas...")
    fix_const_commas()
    
    print("[3] Fixing interface method commas...")
    fix_interface_method_commas()
    
    print("[4] Fixing duplicate package declarations...")
    fix_duplicate_package_decls()
    
    print("[5] Fixing orphan OmniResult structs...")
    fix_orphan_omniresult()
    
    print("[6] Fixing missing closing braces...")
    fix_missing_closing_braces()
    
    print("[7] Fixing printf trailing commas...")
    fix_printf_commas()
    
    print("[8] Fixing string-as-error values...")
    fix_string_as_error()
    
    print(f"\nSUMMARY: {fixes_applied} fixes across {files_fixed} files")
    print("=" * 70)

if __name__ == "__main__":
    main()
