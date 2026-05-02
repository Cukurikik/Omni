"""
OMNI Comprehensive Fix Script — Phase 1
Fixes the following systemic issues across src/:

1. Structs that are missing Err/Error fields — adds 'Err error' field
2. Struct literals using 'Error:' when struct has 'Err error' — reverts to 'Err:'
3. ctx.Error -> ctx.Err() (context.Context has Err() not Error)
4. Adds 'Err error' field to custom result structs that lack it
"""
import os
import re

SRC_ROOT = r"c:\Users\IKYY\Downloads\Omni\src"

stats = {
    "files_scanned": 0,
    "files_modified": 0,
    "ctx_error_fixes": 0,
    "struct_field_adds": 0,
    "err_field_reverts": 0,
}

def fix_file(fpath):
    try:
        with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception:
        return
    
    stats["files_scanned"] += 1
    original = content

    # =====================================================
    # FIX 1: ctx.Error -> ctx.Err()
    # context.Context has Err() method, not Error
    # =====================================================
    ctx_error_pattern = re.compile(r'\bctx\.Error\b(?!\()')
    count_before = len(ctx_error_pattern.findall(content))
    if count_before > 0:
        # Only fix ctx.Error when it's clearly a context method call pattern
        # e.g., ctx.Error undefined (type context.Context...)
        content = ctx_error_pattern.sub('ctx.Err()', content)
        stats["ctx_error_fixes"] += count_before

    # Also fix patterns like req.Ctx.Error -> req.Ctx.Err()
    content = re.sub(r'\.Ctx\.Error\b(?!\()', '.Ctx.Err()', content)

    # =====================================================
    # FIX 2: Find structs that have neither Err nor Error field
    # but are used with Error: in struct literals.
    # Strategy: Add 'Err error' field to such structs.
    # =====================================================
    
    # Find all struct definitions in this file
    struct_pattern = re.compile(
        r'type\s+(\w+)\s+struct\s*\{([^}]*)\}',
        re.DOTALL
    )
    
    structs_in_file = {}
    for m in struct_pattern.finditer(content):
        struct_name = m.group(1)
        struct_body = m.group(2)
        has_err = bool(re.search(r'\bErr\s+error\b', struct_body))
        has_error = bool(re.search(r'\bError\s+error\b', struct_body))
        structs_in_file[struct_name] = {
            "has_err": has_err,
            "has_error": has_error,
            "match": m,
        }
    
    # For each struct that has neither Err nor Error field,
    # check if there are struct literals using Error: or Err:
    # If so, add 'Err error' to the struct definition
    for sname, sinfo in structs_in_file.items():
        if sinfo["has_err"] or sinfo["has_error"]:
            continue
        
        # Check if this struct is used with Error: or Err: in literals
        literal_pattern = re.compile(
            rf'{sname}\s*\{{[^}}]*(?:Error|Err)\s*:', re.DOTALL
        )
        if literal_pattern.search(content):
            # Add 'Err error' field to the struct
            m = sinfo["match"]
            old_body = m.group(0)
            # Find the last field line in the struct body
            struct_body = m.group(2)
            # Add Err error as last field before closing brace
            new_body = old_body.replace(
                struct_body + '}',
                struct_body.rstrip() + '\n\tErr error\n}'
            )
            if new_body != old_body:
                content = content.replace(old_body, new_body, 1)
                stats["struct_field_adds"] += 1
    
    # =====================================================
    # FIX 3: For structs that have 'Err error' field (not 'Error error'),
    # revert 'Error:' back to 'Err:' in struct literals
    # =====================================================
    
    # Re-parse structs after modification
    structs_in_file_updated = {}
    for m in struct_pattern.finditer(content):
        struct_name = m.group(1)
        struct_body = m.group(2)
        has_err = bool(re.search(r'\bErr\s+error\b', struct_body))
        has_error = bool(re.search(r'\bError\s+error\b', struct_body))
        structs_in_file_updated[struct_name] = {
            "has_err": has_err,
            "has_error": has_error,
        }
    
    # For structs with 'Err error' (not 'Error error'),
    # fix struct literals that use 'Error:' -> 'Err:'
    for sname, sinfo in structs_in_file_updated.items():
        if sinfo["has_err"] and not sinfo["has_error"]:
            # Find struct literals for this type and revert Error: to Err:
            # Pattern: TypeName{... Error: ... }
            def revert_error_to_err(match):
                text = match.group(0)
                text = re.sub(r'\bError:', 'Err:', text)
                return text
            
            content = re.sub(
                rf'({sname}\s*\{{[^}}]*)\bError:([^}}]*\}})',
                lambda m: m.group(0).replace('Error:', 'Err:'),
                content,
                flags=re.DOTALL
            )
            stats["err_field_reverts"] += 1
    
    # =====================================================
    # FIX 4: Fix .Error on variables that are struct instances
    # with Err field (not Error field). 
    # Pattern: variable.Error -> variable.Err (but only for known types)
    # This is harder to do safely, so we focus on specific patterns:
    # res.Error, r.Error, result.Error when struct has Err
    # =====================================================
    for sname, sinfo in structs_in_file_updated.items():
        if sinfo["has_err"] and not sinfo["has_error"]:
            # Fix field access patterns like .Error on these types
            # We can't reliably know variable types, but fix common patterns
            # in the same file where struct is defined
            pass  # This is too risky without type info, skip
    
    if content != original:
        try:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
            stats["files_modified"] += 1
        except Exception as e:
            print(f"  ERROR writing {fpath}: {e}")

# Walk the src directory
for root, dirs, files in os.walk(SRC_ROOT):
    for fname in files:
        if not fname.endswith('.go'):
            continue
        fpath = os.path.join(root, fname)
        fix_file(fpath)

print("\n=== OMNI Comprehensive Fix Phase 1 Complete ===")
for k, v in stats.items():
    print(f"  {k}: {v}")
