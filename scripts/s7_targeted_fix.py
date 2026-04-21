# -*- coding: utf-8 -*-
"""
OMNI SEMESTER 7 — TARGETED FIX FOR 6 BROKEN FILES
Fixes syntax errors caused by mass remediation script inserting
docstrings/diagnostics into nested classes and after @staticmethod decorators.
"""
import os
import re
import sys

ENGINE_DIR = os.path.join("src", "compute", "python_core", "system")

def fix_staticmethod_docstring(lines):
    """Fix cases where docstring was inserted between @staticmethod and def."""
    fixed = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Pattern: @staticmethod followed by a docstring (wrong placement)
        if line.strip() == "@staticmethod" and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line.startswith('"""') and next_line.endswith('"""'):
                # Skip the wrongly placed docstring
                fixed.append(line)
                i += 2  # skip @staticmethod and the bad docstring
                continue
        fixed.append(line)
        i += 1
    return fixed


def remove_nested_class_injections(lines):
    """Remove docstrings and diagnostics() methods injected into nested classes
    (classes defined inside methods with deeper indentation)."""
    fixed = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Detect a class line that is deeply indented (nested inside a method)
        # These are classes with >= 12 spaces (3+ levels of indentation)
        indent = len(line) - len(line.lstrip())

        # Check if this is a nested class line followed by a wrongly-indented docstring
        if stripped.startswith("class ") and stripped.endswith(":") and indent >= 12:
            fixed.append(line)
            i += 1
            # Check if next line is a wrongly-indented docstring at column 4
            if i < len(lines):
                next_stripped = lines[i].strip()
                next_indent = len(lines[i]) - len(lines[i].lstrip())
                if next_stripped.startswith('"""') and next_indent < indent:
                    # This is a wrongly injected docstring - skip it
                    i += 1
                    # Now check for wrongly injected diagnostics block
                    # Skip any blank lines first
                    while i < len(lines) and lines[i].strip() == "":
                        i += 1
                    # Check if there's a diagnostics method at wrong indent
                    if i < len(lines) and lines[i].strip().startswith("def diagnostics(self)"):
                        diag_indent = len(lines[i]) - len(lines[i].lstrip())
                        if diag_indent < indent:
                            # Skip the entire diagnostics block
                            i += 1  # skip def line
                            if i < len(lines) and lines[i].strip().startswith('"""'):
                                i += 1  # skip docstring
                            # Skip return block
                            while i < len(lines) and lines[i].strip() != "" and not lines[i].strip().startswith("class ") and not lines[i].strip().startswith("def ") and not lines[i].strip().startswith("#"):
                                if len(lines[i]) - len(lines[i].lstrip()) >= diag_indent or lines[i].strip() == "":
                                    i += 1
                                else:
                                    break
                            # Skip trailing blank line
                            while i < len(lines) and lines[i].strip() == "":
                                i += 1
            continue

        # Also detect standalone wrong-indent docstrings after nested class fields
        # Pattern: a line at indent 4 that is a docstring, but previous context is inside a method
        fixed.append(line)
        i += 1

    return fixed


def fix_file(fpath, fname):
    """Apply all targeted fixes to a file."""
    with open(fpath, "r", encoding="utf-8") as f:
        original = f.read()
        lines = original.split("\n")

    # Convert to lines with newlines for processing
    with open(fpath, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()

    fixed_lines = fix_staticmethod_docstring(raw_lines)
    fixed_lines = remove_nested_class_injections(fixed_lines)

    new_content = "".join(fixed_lines)

    if new_content != original:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False


def main():
    # Only fix the 6 broken files
    broken_files = [
        "omni_autopkg_engine.py",
        "omni_bastille_engine.py",
        "omni_clap_plugin_engine.py",
        "omni_flaui_engine.py",
        "omni_lstm_ar_engine.py",
        "omni_robotgo_engine.py",
    ]

    print("=" * 70)
    print("  TARGETED SYNTAX FIX FOR 6 BROKEN FILES")
    print("=" * 70)

    for fname in broken_files:
        fpath = os.path.join(ENGINE_DIR, fname)
        if not os.path.exists(fpath):
            print("  [SKIP] {} not found".format(fname))
            continue
        result = fix_file(fpath, fname)
        if result:
            print("  [FIXED] {}".format(fname))
        else:
            print("  [NO CHANGE] {}".format(fname))

    print("=" * 70)
    print("  Verifying syntax of fixed files...")
    
    import ast
    all_ok = True
    for fname in broken_files:
        fpath = os.path.join(ENGINE_DIR, fname)
        if not os.path.exists(fpath):
            continue
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                ast.parse(f.read())
            print("  [OK] {} parses successfully".format(fname))
        except SyntaxError as e:
            print("  [!!] {} STILL BROKEN: {}".format(fname, e))
            all_ok = False

    print("=" * 70)
    if all_ok:
        print("  ALL 6 FILES FIXED SUCCESSFULLY")
    else:
        print("  SOME FILES STILL NEED MANUAL FIX")
    print("=" * 70)


if __name__ == "__main__":
    main()
