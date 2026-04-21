"""
Fix ENGINE_VERSION for files that were missed or broken by first pass.
"""
import os
import ast
import re
import sys

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))


def fix_broken_version_insertions(fpath, fname):
    """Fix cases where ENGINE_VERSION was inserted inside an import block."""
    with open(fpath, "r", encoding="utf-8", errors="replace") as f:
        source = f.read()

    # Check if file has syntax error
    try:
        ast.parse(source)
        return 0  # No syntax error
    except SyntaxError:
        pass

    # Look for VERSION inside a multi-line import
    lines = source.split("\n")
    # Pattern: find ENGINE_VERSION line between open paren import and close paren
    in_paren = False
    paren_depth = 0
    version_in_import = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Track parentheses
        paren_depth += stripped.count("(") - stripped.count(")")
        
        if paren_depth > 0 and "ENGINE_VERSION" in stripped:
            version_in_import = i
            break
    
    if version_in_import is not None:
        # Remove it from inside the import
        removed_line = lines.pop(version_in_import)
        # Also remove blank lines around it
        while version_in_import < len(lines) and lines[version_in_import].strip() == "":
            lines.pop(version_in_import)
        if version_in_import > 0 and lines[version_in_import - 1].strip() == "":
            lines.pop(version_in_import - 1)
        
        # Find end of imports
        insert_at = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(("import ", "from ", "try:", "except")):
                insert_at = i + 1
            elif stripped and not stripped.startswith("#") and not stripped.startswith(('"""', "'''", '"', "'")) and i > 5:
                break

        if 'ENGINE_VERSION' not in "\n".join(lines):
            lines.insert(insert_at, "")
            lines.insert(insert_at + 1, 'ENGINE_VERSION = "1.0.0-omni"')
            lines.insert(insert_at + 2, "")

        with open(fpath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return 1
    
    return 0


def add_version_to_file(fpath, fname):
    """Add ENGINE_VERSION constant after imports if missing."""
    with open(fpath, "r", encoding="utf-8", errors="replace") as f:
        source = f.read()

    # Skip if already has VERSION
    if "ENGINE_VERSION" in source or "engine_version" in source.lower():
        return 0

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return 0

    # check if already has version via AST
    for n in ast.iter_child_nodes(tree):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and "VERSION" in t.id.upper():
                    return 0

    lines = source.split("\n")
    
    # Find the last import line
    last_import = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(("import ", "from ")):
            last_import = i
        elif stripped.startswith("try:"):
            # Check if next lines have imports
            for j in range(i+1, min(i+5, len(lines))):
                if lines[j].strip().startswith(("import ", "from ")):
                    last_import = j
        elif stripped.startswith("except"):
            for j in range(i+1, min(i+5, len(lines))):
                if lines[j].strip().startswith(("import ", "from ")):
                    last_import = j
                elif lines[j].strip() and not lines[j].strip().startswith("#"):
                    last_import = max(last_import, j)
                    break

    # Walk forward past any trailing parens on multi-line imports
    paren_depth = 0
    for i in range(last_import, len(lines)):
        paren_depth += lines[i].count("(") - lines[i].count(")")
        if paren_depth <= 0 and i >= last_import:
            last_import = i
            break

    insert_at = last_import + 1
    
    lines.insert(insert_at, "")
    lines.insert(insert_at + 1, 'ENGINE_VERSION = "1.0.0-omni"')

    with open(fpath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    return 1


def main():
    files = sorted([
        f for f in os.listdir(ENGINE_DIR)
        if f.startswith("omni_") and f.endswith(".py")
    ])

    print(f"VERSION FIX PASS 2: {len(files)} files")
    
    total_broken = 0
    total_added = 0

    for fname in files:
        fpath = os.path.join(ENGINE_DIR, fname)
        
        # First fix any broken insertions
        b = fix_broken_version_insertions(fpath, fname)
        total_broken += b
        if b > 0:
            print(f"  [FIXED-BROKEN] {fname}")
        
        # Then add if still missing
        a = add_version_to_file(fpath, fname)
        total_added += a
        if a > 0:
            print(f"  [ADDED] {fname}")

    print(f"\nBroken insertions fixed: {total_broken}")
    print(f"New VERSION added: {total_added}")
    print(f"Total: {total_broken + total_added}")


if __name__ == "__main__":
    main()
