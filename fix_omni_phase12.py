#!/usr/bin/env python3
"""
OMNI Phase 12 — Fix "unexpected newline in composite literal" errors.

These are cases where a multi-line struct literal is missing a trailing comma
on a field value line, e.g.:

    SomeStruct{
        Field1: value1    // <- missing comma here
        Field2: value2,
    }

Also handles cases where function return statements in struct literals
are missing commas.
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

def add_missing_literal_commas():
    """Add missing commas in composite literal (struct/map/slice) multi-line expressions."""
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
            lines = content.split('\n')
            new_lines = []
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                if i + 1 < len(lines):
                    next_stripped = lines[i + 1].strip()
                    
                    # Check if this is a struct/map field value line missing comma
                    # Pattern: FieldName: value\n  (where next line is another field or })
                    if (stripped and 
                        not stripped.endswith(',') and 
                        not stripped.endswith('{') and
                        not stripped.endswith('(') and
                        not stripped.endswith('*/') and
                        not stripped.startswith('//') and
                        not stripped.startswith('/*') and
                        stripped != '}' and
                        stripped != ')' and
                        stripped != '},'):
                        
                        # This line has Field: value pattern
                        has_field_colon = ':' in stripped and not stripped.startswith('//')
                        
                        # Next line is a closing brace or another field
                        next_is_closing = next_stripped in ('}', '},', '})', ')')
                        next_is_field = re.match(r'\w[\w.]*\s*:', next_stripped) is not None
                        
                        if has_field_colon and (next_is_closing or next_is_field):
                            # Check that it's not a label: or case:
                            field_part = stripped.split(':')[0].strip()
                            if (not field_part.startswith('case ') and 
                                field_part != 'default' and
                                not field_part.startswith('func') and
                                not stripped.endswith(':')):
                                line = line.rstrip() + ','
                        
                        # Also handle map literal values: "key": value
                        if stripped.startswith('"') and ':' in stripped and (next_is_closing or next_is_field):
                            if not stripped.endswith(','):
                                line = line.rstrip() + ','
                
                new_lines.append(line)
            
            content = '\n'.join(new_lines)
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def fix_more_premature_braces():
    """Another pass at removing premature closing braces."""
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
            lines = content.split('\n')
            
            # Look for patterns: } followed by indented code that references local vars
            new_lines = []
            i = 0
            while i < len(lines):
                line = lines[i]
                stripped = line.strip()
                
                if stripped == '}':
                    # Count depth after this line
                    depth_before = 0
                    for j in range(i):
                        depth_before += lines[j].count('{') - lines[j].count('}')
                    
                    depth_after = depth_before - 1  # After this }
                    
                    if depth_after == 0:
                        # This closes a top-level block
                        # Check if next non-empty lines are indented (orphaned code)
                        orphan_start = -1
                        for k in range(i + 1, min(i + 15, len(lines))):
                            ks = lines[k].strip()
                            if ks == '':
                                continue
                            if ks.startswith('//'):
                                continue
                            if lines[k].startswith('\t') and not ks.startswith('func ') and not ks.startswith('type '):
                                orphan_start = k
                            break
                        
                        if orphan_start >= 0:
                            # Remove this premature } 
                            i += 1
                            continue
                
                new_lines.append(line)
                i += 1
            
            content = '\n'.join(new_lines)
            
            # Re-balance braces
            open_count = content.count('{')
            close_count = content.count('}')
            if open_count > close_count:
                diff = open_count - close_count
                content = content.rstrip() + '\n'
                for _ in range(diff):
                    content += '}\n'
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def main():
    print("=" * 70)
    print("OMNI PHASE 12 — Composite Literal Commas + Brace V3")
    print("=" * 70)
    
    print("\n[1] Adding missing commas in composite literals...")
    add_missing_literal_commas()
    
    print("[2] Fixing more premature braces...")
    fix_more_premature_braces()
    
    print(f"\nSUMMARY: {fixes_applied} fixes across {files_fixed} files")
    print("=" * 70)

if __name__ == "__main__":
    main()
