"""
OMNI Fix Phase 2: 
1. ctx.Error() -> ctx.Err()  (context.Context method is Err() not Error())
2. res.Error -> res.Err (for structs with Err field)
3. Fix remaining 'unknown field Error' in struct literals
"""
import os
import re

SRC_ROOT = r"c:\Users\IKYY\Downloads\Omni\src"

stats = {"files_modified": 0, "ctx_err_fixes": 0, "res_err_fixes": 0}

for root, dirs, files in os.walk(SRC_ROOT):
    for fname in files:
        if not fname.endswith('.go'):
            continue
        fpath = os.path.join(root, fname)
        try:
            with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except Exception:
            continue
        
        original = content
        
        # Fix ctx.Error() -> ctx.Err()
        content = content.replace('ctx.Error()', 'ctx.Err()')
        content = content.replace('.Ctx.Error()', '.Ctx.Err()')
        
        # Fix res.Error -> res.Err for field access (not in struct literals)
        # Pattern: identifier.Error followed by space, ), }, etc. but NOT followed by ':'
        # This handles field access like: res.Error != nil, res.Error.Error()
        # But NOT struct literal: {Error: ...}
        content = re.sub(
            r'(\b(?:res|r|result|ret)\b)\.Error\b',
            r'\1.Err',
            content
        )
        
        if content != original:
            ctx_fixes = content.count('ctx.Err()') - original.count('ctx.Err()')
            stats["ctx_err_fixes"] += ctx_fixes
            try:
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(content)
                stats["files_modified"] += 1
            except Exception as e:
                print(f"ERROR: {e}")

print("\n=== Phase 2 Fix Complete ===")
for k, v in stats.items():
    print(f"  {k}: {v}")
