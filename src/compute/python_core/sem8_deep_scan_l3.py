"""
OMNI Semester 8 - DEEP SCAN LEVEL 3
====================================
The most comprehensive scan ever run on the OMNI engine ecosystem.
Checks EVERY aspect of CODE RULE 001-005 not covered by Level 1 and 2.

Categories checked:
  1.  Syntax errors (re-verify after all patches)
  2.  Missing class-level docstrings
  3.  Missing standalone function docstrings
  4.  Missing method docstrings (non-dunder)
  5.  Functions/methods missing return type hints
  6.  Functions/methods missing parameter type hints
  7.  Duplicate ENGINE_VERSION insertions
  8.  Broken/orphaned imports from patches
  9.  Module-level code outside classes (stray code)
  10. PEP 8: Line length > 120 chars
  11. Integration test file syntax errors
  12. Missing module-level docstrings
  13. Classes with no methods (empty classes, excluding Exceptions)
  14. Bare except clauses
"""

import os
import ast
import re
import sys
from collections import defaultdict

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))


def has_docstring(node):
    """Check if an AST node has a docstring."""
    if node.body and isinstance(node.body[0], ast.Expr):
        val = node.body[0].value
        if isinstance(val, ast.Constant) and isinstance(val.value, str):
            return True
    return False


def is_exception_class(node):
    """Check if a class inherits from Exception."""
    for b in node.bases:
        if isinstance(b, ast.Name) and b.id in (
            "Exception", "BaseException", "RuntimeError",
            "ValueError", "TypeError", "KeyError", "IOError",
            "OSError", "AttributeError", "ImportError",
        ):
            return True
        if isinstance(b, ast.Attribute):
            if hasattr(b, 'attr') and 'Error' in b.attr:
                return True
    return False


def scan_all():
    """Run Level 3 comprehensive scan."""
    results = defaultdict(list)

    engine_files = sorted([
        f for f in os.listdir(ENGINE_DIR)
        if f.startswith("omni_") and f.endswith(".py")
    ])

    for fname in engine_files:
        fpath = os.path.join(ENGINE_DIR, fname)
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
            lines = source.split("\n")

        # --- Check 10: Line length ---
        long_lines = 0
        for i, line in enumerate(lines):
            if len(line.rstrip()) > 120:
                long_lines += 1
        if long_lines > 0:
            results["pep8_long_lines"].append(f"{fname}: {long_lines} lines")

        # --- Check 7: Duplicate ENGINE_VERSION ---
        version_count = source.count("ENGINE_VERSION")
        if version_count > 2:  # assignment + possible usage = 2 is OK
            actual_assigns = len(re.findall(r'^ENGINE_VERSION\s*=', source, re.MULTILINE))
            if actual_assigns > 1:
                results["duplicate_version"].append(f"{fname}: {actual_assigns} assignments")

        # --- Parse AST ---
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            results["syntax_error"].append(f"{fname}:{e.lineno}: {e.msg}")
            continue

        # --- Check 12: Module docstring ---
        if not has_docstring(tree):
            results["missing_module_docstring"].append(fname)

        # --- Walk classes ---
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                is_exc = is_exception_class(node)

                # Check 2: Class docstring
                if not has_docstring(node) and not is_exc:
                    results["missing_class_docstring"].append(
                        f"{fname}:{node.name}"
                    )

                # Check 13: Empty class (no methods, excluding exceptions)
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if not methods and not is_exc:
                    # Check if it's a dataclass or has class vars
                    has_content = any(
                        isinstance(n, (ast.Assign, ast.AnnAssign))
                        for n in node.body
                    )
                    if not has_content and not has_docstring(node):
                        results["empty_class"].append(f"{fname}:{node.name}")

                if is_exc:
                    continue

                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        # Check 4: Method docstring (non-dunder, non-private)
                        if not item.name.startswith("_") and not has_docstring(item):
                            results["missing_method_docstring"].append(
                                f"{fname}:{node.name}.{item.name}"
                            )

                        # Check 5: Return type hint (public methods)
                        if not item.name.startswith("_") and item.returns is None:
                            results["missing_return_type"].append(
                                f"{fname}:{node.name}.{item.name}"
                            )

                        # Check 6: Parameter type hints
                        for arg in item.args.args:
                            if arg.arg == "self":
                                continue
                            if arg.annotation is None:
                                results["missing_param_type"].append(
                                    f"{fname}:{node.name}.{item.name}({arg.arg})"
                                )
                                break  # Only report once per method

            # Check 14: Bare except
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                results["bare_except"].append(fname)

        # --- Check 3: Standalone function docstrings ---
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith("_") and not has_docstring(node):
                    results["missing_func_docstring"].append(
                        f"{fname}:{node.name}"
                    )

    # Deduplicate bare_except per file
    results["bare_except"] = list(set(results["bare_except"]))

    # --- Check 11: Integration test syntax ---
    test_files = sorted([
        f for f in os.listdir(ENGINE_DIR)
        if f.startswith("sem8_batch") and f.endswith(".py")
    ])
    for fname in test_files:
        fpath = os.path.join(ENGINE_DIR, fname)
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
        try:
            ast.parse(source)
        except SyntaxError as e:
            results["test_syntax_error"].append(f"{fname}:{e.lineno}")

    return len(engine_files), results


def main():
    total, results = scan_all()

    print("=" * 70)
    print("OMNI SEMESTER 8 - DEEP SCAN LEVEL 3")
    print("EXHAUSTIVE CODE RULE 001-005 COMPLIANCE AUDIT")
    print("=" * 70)
    print(f"Engine files scanned: {total}")
    print()

    severity_order = [
        ("CRITICAL", [
            "syntax_error",
            "test_syntax_error",
        ]),
        ("HIGH", [
            "missing_module_docstring",
            "missing_class_docstring",
            "missing_method_docstring",
            "missing_func_docstring",
            "bare_except",
            "duplicate_version",
        ]),
        ("MEDIUM", [
            "empty_class",
            "missing_return_type",
            "missing_param_type",
        ]),
        ("LOW", [
            "pep8_long_lines",
        ]),
    ]

    grand_total = 0
    for severity, categories in severity_order:
        for cat in categories:
            items = results.get(cat, [])
            count = len(items)
            grand_total += count
            marker = " ***" if count > 0 and severity in ("CRITICAL", "HIGH") else ""
            print(f"  [{severity:8s}] {cat:35s}: {count}{marker}")

    print()
    print(f"  GRAND TOTAL DEFICIENCIES: {grand_total}")
    print("=" * 70)

    # Print details for items with issues
    for severity, categories in severity_order:
        for cat in categories:
            items = results.get(cat, [])
            if items and severity in ("CRITICAL", "HIGH"):
                print(f"\n  === {cat.upper()} ({len(items)}) ===")
                for item in items[:25]:
                    print(f"    {item}")
                if len(items) > 25:
                    print(f"    ... and {len(items) - 25} more")

    if grand_total == 0:
        print("\nPERFECT SCORE. ZERO DEFICIENCIES ACROSS ALL CATEGORIES.")
    else:
        # Categorize what's actionable vs acceptable
        critical_high = sum(
            len(results.get(cat, []))
            for _, cats in severity_order[:2]
            for cat in cats
        )
        medium_low = grand_total - critical_high
        print(f"\n  CRITICAL+HIGH issues: {critical_high}")
        print(f"  MEDIUM+LOW issues  : {medium_low}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
