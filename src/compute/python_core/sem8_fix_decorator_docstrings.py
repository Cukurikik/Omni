"""
Fix docstrings incorrectly placed between decorators and method definitions.
Pattern: @decorator \\n docstring \\n def method  ->  @decorator \\n def method \\n docstring
"""
import os
import ast
import re
import sys

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))


def fix_decorator_docstrings(fpath, fname):
    """Move docstrings from between decorator and def to inside the method body."""
    with open(fpath, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    changed = False
    i = 0
    while i < len(lines) - 2:
        curr = lines[i].rstrip()
        next1 = lines[i + 1].rstrip() if i + 1 < len(lines) else ""
        next2 = lines[i + 2].rstrip() if i + 2 < len(lines) else ""

        curr_s = curr.strip()
        next1_s = next1.strip()
        next2_s = next2.strip()

        # Pattern: @decorator \n """docstring""" \n def method(...)
        if curr_s.startswith("@") and \
           next1_s.startswith('"""') and next1_s.endswith('"""') and \
           next2_s.startswith("def "):

            # Extract the docstring and its indentation
            docstring_line = lines[i + 1]
            # Get the indentation of the def line's body
            def_line = lines[i + 2]
            def_indent = re.match(r'^(\s*)', def_line).group(1)
            body_indent = def_indent + "    "

            # Check if the def is a one-liner like: def ok(cls, val): return cls(val)
            if ":" in next2_s:
                colon_pos = next2_s.index(":")
                after_colon = next2_s[colon_pos + 1:].strip()

                if after_colon:
                    # It's a one-liner: def method(...): body
                    # Convert to multi-line with docstring
                    def_part = next2_s[:colon_pos + 1]
                    body_part = after_colon

                    new_lines = [
                        lines[i],  # @decorator
                        def_indent + def_part + "\n",  # def method(...):
                        body_indent + next1_s + "\n",  # """docstring"""
                        body_indent + body_part + "\n",  # body
                    ]

                    lines[i:i + 3] = new_lines
                    changed = True
                    i += len(new_lines)
                    continue
                else:
                    # Multi-line def: move docstring after the def line
                    # Find the real body start
                    docstring_text = next1_s
                    # Remove the misplaced docstring
                    lines.pop(i + 1)

                    # Find the first body line after def
                    j = i + 1  # now pointing to def line (after pop)
                    # Check if def spans multiple lines (parentheses)
                    paren_depth = lines[j].count("(") - lines[j].count(")")
                    while paren_depth > 0 and j + 1 < len(lines):
                        j += 1
                        paren_depth += lines[j].count("(") - lines[j].count(")")

                    # j now points to the closing line of def
                    # Insert docstring after it
                    lines.insert(j + 1, body_indent + docstring_text + "\n")
                    changed = True
                    i = j + 2
                    continue

        i += 1

    if changed:
        new_source = "".join(lines)
        try:
            ast.parse(new_source)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(new_source)
            return 1
        except SyntaxError as e:
            print(f"  [STILL BROKEN] {fname}:{e.lineno}: {e.msg}")
            return 0

    return 0


def main():
    files = sorted([
        f for f in os.listdir(ENGINE_DIR)
        if f.startswith("omni_") and f.endswith(".py")
    ])

    print("=" * 60)
    print("FIX DECORATOR-DOCSTRING MISPLACEMENT")
    print("=" * 60)

    total_fixed = 0
    still_broken = []

    for fname in files:
        fpath = os.path.join(ENGINE_DIR, fname)

        # Only process files with syntax errors
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
        try:
            ast.parse(source)
            continue
        except SyntaxError:
            pass

        result = fix_decorator_docstrings(fpath, fname)
        if result > 0:
            total_fixed += 1
            print(f"  [FIXED] {fname}")
        else:
            still_broken.append(fname)

    print(f"\nFixed: {total_fixed}")
    if still_broken:
        print(f"Still broken: {len(still_broken)}")
        for f in still_broken:
            print(f"  {f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
