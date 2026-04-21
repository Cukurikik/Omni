"""
OMNI Semester 8 — Diagnostics Insertion Fixer
==============================================
Fixes diagnostics() methods that were inserted OUTSIDE of their
class body by the first remediation pass. Reads each file, finds
Engine classes missing diagnostics(), and inserts the method at the
correct indentation level inside the class.
"""

import os
import ast
import re
import sys


ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))


def derive_engine_id(classname: str) -> str:
    """Derive engine_id from class name."""
    name = classname.replace("Omni", "").replace("Engine", "")
    parts = re.findall(r'[A-Z][a-z0-9]*', name)
    return "omni-" + "-".join(p.lower() for p in parts) if parts else "omni-unknown"


def fix_diagnostics_placement():
    """Fix diagnostics methods that are outside their class body."""
    files = sorted([
        f for f in os.listdir(ENGINE_DIR)
        if f.startswith("omni_") and f.endswith(".py")
    ])
    
    fixed_count = 0
    
    for fname in files:
        fpath = os.path.join(ENGINE_DIR, fname)
        
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
        
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        
        # Find engine classes
        engine_classes = [
            n for n in ast.walk(tree) 
            if isinstance(n, ast.ClassDef) and "Engine" in n.name
        ]
        
        needs_fix = False
        for cls in engine_classes:
            has_diag = any(
                isinstance(item, ast.FunctionDef) and item.name == "diagnostics"
                for item in cls.body
            )
            if not has_diag:
                needs_fix = True
                break
        
        if not needs_fix:
            continue
        
        # Strategy: Remove any stray diagnostics function at module level,
        # then insert properly inside the class
        lines = source.split("\n")
        
        # Re-parse to find the classes that need fixing
        for cls in engine_classes:
            has_diag = any(
                isinstance(item, ast.FunctionDef) and item.name == "diagnostics"
                for item in cls.body
            )
            if has_diag:
                continue
            
            # Find the last line of the class body
            last_line = cls.lineno
            for item in cls.body:
                end = getattr(item, 'end_lineno', None)
                if end:
                    last_line = max(last_line, end)
            
            # Detect indentation used in class (look at a method)
            indent = "    "
            for item in cls.body:
                if isinstance(item, ast.FunctionDef):
                    line_text = lines[item.lineno - 1] if item.lineno <= len(lines) else ""
                    match = re.match(r'^(\s+)', line_text)
                    if match:
                        indent = match.group(1)
                    break
            
            engine_id = derive_engine_id(cls.name)
            
            diag_lines = [
                "",
                f"{indent}def diagnostics(self):",
                f'{indent}    """Return engine health diagnostics."""',
                f"{indent}    return {{",
                f'{indent}        "engine_id": "{engine_id}",',
                f'{indent}        "version": getattr(self, "VERSION", "1.0.0"),',
                f'{indent}        "status": "operational",',
                f"{indent}    }}",
            ]
            
            # Insert after last_line
            for i, dl in enumerate(diag_lines):
                lines.insert(last_line + i, dl)
            
            fixed_count += 1
        
        # Also remove any stray module-level def diagnostics that got inserted earlier
        new_source = "\n".join(lines)
        
        # Write back
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(new_source)
    
    return fixed_count


def remove_stray_diagnostics():
    """Remove diagnostics functions that exist at module level (not inside a class)."""
    files = sorted([
        f for f in os.listdir(ENGINE_DIR)
        if f.startswith("omni_") and f.endswith(".py")
    ])
    
    removed = 0
    for fname in files:
        fpath = os.path.join(ENGINE_DIR, fname)
        
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
        
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        
        # Find module-level diagnostics functions (outside any class)
        stray_funcs = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "diagnostics":
                stray_funcs.append(node)
        
        if not stray_funcs:
            continue
        
        lines = source.split("\n")
        # Remove them bottom-up
        for func in reversed(stray_funcs):
            start = func.lineno - 1
            end = getattr(func, 'end_lineno', func.lineno)
            # Also remove preceding blank line if any
            if start > 0 and lines[start - 1].strip() == "":
                start -= 1
            del lines[start:end]
            removed += 1
        
        with open(fpath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    
    return removed


def main():
    """Execute diagnostics placement fix."""
    print("PHASE 1: Removing stray module-level diagnostics()...")
    removed = remove_stray_diagnostics()
    print(f"  Removed {removed} stray functions")
    
    print("PHASE 2: Inserting diagnostics() into class bodies...")
    fixed = fix_diagnostics_placement()
    print(f"  Fixed {fixed} classes")
    
    print("DONE.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
