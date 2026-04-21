"""
Fix docstrings stuck between @decorator and def.
Uses regex on full source text for maximum reliability.
"""
import os
import ast
import re
import sys

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))


def fix_file(fpath, fname):
    """Fix decorator-docstring-def pattern in a file."""
    with open(fpath, "r", encoding="utf-8", errors="replace") as f:
        source = f.read()

    # Try parsing first
    try:
        ast.parse(source)
        return 0  # No error
    except SyntaxError:
        pass

    # Pattern: @decorator\n    """docstring"""\n    def method(...): one-liner-body
    # Fix: @decorator\n    def method(...):\n        """docstring"""\n        one-liner-body
    pattern = re.compile(
        r'(\s*)(@\w+)\s*\n'           # group 1=indent, group 2=decorator
        r'\s*"""([^"]+)"""\s*\n'       # group 3=docstring content
        r'\s*def\s+(\w+)\(([^)]*)\)(?:\s*->\s*\w+)?\s*:\s*(.+)',  # group 4=name, 5=args, 6=body
        re.MULTILINE
    )

    def replacer(match):
        indent = match.group(1)
        decorator = match.group(2)
        docstring = match.group(3)
        method_name = match.group(4)
        args = match.group(5)
        body = match.group(6).strip()

        # Check for return type
        full_match = match.group(0)
        arrow_match = re.search(r'->\s*(\w+)', full_match)
        ret_type = f" -> {arrow_match.group(1)}" if arrow_match else ""

        return (
            f'{indent}{decorator}\n'
            f'{indent}def {method_name}({args}){ret_type}:\n'
            f'{indent}    """{docstring}"""\n'
            f'{indent}    {body}'
        )

    new_source = pattern.sub(replacer, source)

    # Also handle multi-line def (no one-liner body)
    pattern2 = re.compile(
        r'(\s*)(@\w+)\s*\n'           # indent + decorator
        r'\s*"""([^"]+)"""\s*\n'       # docstring
        r'(\s*def\s+\w+\([^)]*\)(?:\s*->\s*\w+)?\s*:\s*\n)',  # def line with newline
        re.MULTILINE
    )

    def replacer2(match):
        indent = match.group(1)
        decorator = match.group(2)
        docstring = match.group(3)
        def_line = match.group(4)
        body_indent = indent + "    "

        return (
            f'{indent}{decorator}\n'
            f'{def_line}'
            f'{body_indent}"""{docstring}"""\n'
        )

    new_source = pattern2.sub(replacer2, new_source)

    if new_source == source:
        return 0

    try:
        ast.parse(new_source)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(new_source)
        return 1
    except SyntaxError as e:
        print(f"    Still broken after regex: {fname}:{e.lineno}: {e.msg}")
        # Dump context around error
        lines = new_source.split("\n")
        for li in range(max(0, e.lineno - 3), min(len(lines), e.lineno + 2)):
            marker = ">>>" if li == e.lineno - 1 else "   "
            print(f"    {marker} {li+1}: {lines[li][:100]}")
        return 0


def main():
    files = sorted([
        f for f in os.listdir(ENGINE_DIR)
        if f.startswith("omni_") and f.endswith(".py")
    ])

    print("FIX DECORATOR-DOCSTRING (REGEX PASS)")
    print("=" * 60)

    total = 0
    broken = []
    for fname in files:
        fpath = os.path.join(ENGINE_DIR, fname)
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            src = f.read()
        try:
            ast.parse(src)
            continue
        except SyntaxError:
            pass

        r = fix_file(fpath, fname)
        if r > 0:
            total += 1
            print(f"  [FIXED] {fname}")
        else:
            broken.append(fname)

    print(f"\nFixed: {total}")
    if broken:
        print(f"Still broken: {len(broken)}")
        for f in broken:
            print(f"  {f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
