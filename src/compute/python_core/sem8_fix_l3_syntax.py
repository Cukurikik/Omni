"""
Fix syntax errors caused by Level 3 docstring insertions.
Usually caused by docstrings inserted inside dataclass field definitions
or enum member lists.
"""
import os
import ast
import re
import sys

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))


def fix_syntax_errors():
    """Find and fix syntax errors from docstring insertions."""
    files = sorted([
        f for f in os.listdir(ENGINE_DIR)
        if f.startswith("omni_") and f.endswith(".py")
    ])

    fixed = 0
    for fname in files:
        fpath = os.path.join(ENGINE_DIR, fname)
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()

        try:
            ast.parse(source)
            continue  # No syntax error
        except SyntaxError as e:
            pass

        lines = source.split("\n")
        # Strategy: find docstrings that were inserted at wrong positions
        # Pattern: a docstring line followed by something that suggests it's
        # inside a dataclass or enum (field assignment, enum member)
        changed = False
        i = 0
        while i < len(lines):
            stripped = lines[i].strip()
            # Check if this line is a standalone docstring
            if stripped.startswith('"""') and stripped.endswith('"""') and len(stripped) > 6:
                # Check context: what's before and after?
                # If the line BEFORE is a class/dataclass field or enum member
                # and line AFTER is also, we inserted docstring in wrong place
                prev_line = lines[i-1].strip() if i > 0 else ""
                next_line = lines[i+1].strip() if i+1 < len(lines) else ""

                # If previous line has a field assignment (name: type = val)
                # or an enum member, this docstring is misplaced
                is_misplaced = False

                # After a dataclass field: "name: Type = value" or "name: Type"
                if re.match(r'^\w+\s*:\s*\w+.*=', prev_line):
                    is_misplaced = True
                elif re.match(r'^\w+\s*:\s*\w+', prev_line) and not prev_line.startswith("def ") and not prev_line.startswith("class "):
                    is_misplaced = True
                # After an enum member: "NAME = value"
                elif re.match(r'^[A-Z_]+\s*=\s*', prev_line):
                    is_misplaced = True
                # Before a field assignment (next line is a field def)
                elif re.match(r'^\w+\s*:\s*\w+', next_line) and not next_line.startswith("def ") and not next_line.startswith("class "):
                    # Check if prev is also a field or class def
                    if re.match(r'^\w+\s*:\s*\w+', prev_line) or prev_line.startswith("class ") or prev_line == "":
                        is_misplaced = True

                if is_misplaced:
                    # Remove this misplaced docstring
                    lines.pop(i)
                    # Also remove blank line if one was left
                    if i < len(lines) and lines[i].strip() == "":
                        pass  # leave it
                    changed = True
                    continue

            i += 1

        if changed:
            new_source = "\n".join(lines)
            try:
                ast.parse(new_source)
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(new_source)
                fixed += 1
                print(f"  [FIXED] {fname}")
            except SyntaxError as e:
                print(f"  [STILL BROKEN] {fname}:{e.lineno} - needs manual fix")
                # Try more aggressive: remove ALL misplaced docstrings
                lines2 = source.split("\n")
                removals = []
                for j in range(len(lines2)):
                    s = lines2[j].strip()
                    if s.startswith('"""') and s.endswith('"""') and len(s) > 6:
                        # Check if within a dataclass or enum body
                        prev = lines2[j-1].strip() if j > 0 else ""
                        nxt = lines2[j+1].strip() if j+1 < len(lines2) else ""
                        # If surrounded by field/enum definitions
                        if (re.match(r'^\w+\s*[=:]', prev) or prev == "") and \
                           (re.match(r'^\w+\s*[=:]', nxt) or nxt == "" or nxt.startswith("def ")):
                            removals.append(j)
                
                for j in reversed(removals):
                    lines2.pop(j)
                
                new_source2 = "\n".join(lines2)
                try:
                    ast.parse(new_source2)
                    with open(fpath, "w", encoding="utf-8") as f:
                        f.write(new_source2)
                    fixed += 1
                    print(f"  [FIXED-AGGRESSIVE] {fname}")
                except SyntaxError as e2:
                    print(f"  [FAILED] {fname}:{e2.lineno}")

    return fixed


def main():
    print("=" * 60)
    print("FIXING L3 SYNTAX ERRORS")
    print("=" * 60)
    fixed = fix_syntax_errors()
    print(f"\nFixed: {fixed} files")


if __name__ == "__main__":
    main()
