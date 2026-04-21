"""
OMNI Semester 8 — Deep Level 2 Compliance Scanner
===================================================
Scans all omni_*_engine.py files for CODE RULE 001-005 compliance:
  1. Syntax errors
  2. Missing type hints (return types on public methods)
  3. Missing __init__ docstrings
  4. Bare except clauses (non-monadic error handling)
  5. Hardcoded credentials
  6. Missing ENGINE_VERSION constant
  7. Empty/placeholder methods (pass/...)
  8. TODO/FIXME/HACK comments
  9. Missing integration test suites per batch
 10. Missing batch diagnostics scripts
"""

import os
import ast
import re
import sys
from collections import defaultdict


ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))

# Patterns
CRED_PATTERN = re.compile(
    r"""(?:password|secret|api_key|token)\s*=\s*['"][^'"]{8,}['"]""",
    re.IGNORECASE,
)
TODO_PATTERN = re.compile(r"#\s*(TODO|FIXME|HACK|XXX|TEMP)\b", re.IGNORECASE)


def has_docstring(node):
    """Check if an AST node has a docstring."""
    if node.body and isinstance(node.body[0], ast.Expr):
        val = node.body[0].value
        if isinstance(val, ast.Constant) and isinstance(val.value, str):
            return True
    return False


def scan_engines():
    """Run comprehensive compliance scan on all engine files."""
    results = {
        "syntax_error": [],
        "missing_init_docstring": [],
        "bare_except": [],
        "hardcoded_creds": [],
        "missing_version": [],
        "empty_methods": [],
        "todo_fixme": [],
        "missing_return_type": [],
    }

    total = 0
    for fname in sorted(os.listdir(ENGINE_DIR)):
        if not fname.startswith("omni_") or not fname.endswith(".py"):
            continue
        total += 1
        fpath = os.path.join(ENGINE_DIR, fname)

        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
            lines = source.split("\n")

        # TODO/FIXME scan
        for i, line in enumerate(lines):
            if TODO_PATTERN.search(line):
                results["todo_fixme"].append(f"{fname}:{i+1}")

        # Hardcoded credentials scan
        for i, line in enumerate(lines):
            if CRED_PATTERN.search(line):
                results["hardcoded_creds"].append(f"{fname}:{i+1}")

        # Parse AST
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            results["syntax_error"].append(f"{fname}:{e.lineno}")
            continue

        # Check for VERSION constant
        has_ver = False
        for n in ast.iter_child_nodes(tree):
            if isinstance(n, ast.Assign):
                for t in n.targets:
                    if isinstance(t, ast.Name) and "VERSION" in t.id.upper():
                        has_ver = True
        if not has_ver:
            results["missing_version"].append(fname)

        # Walk classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        # __init__ docstring check
                        if item.name == "__init__" and not has_docstring(item):
                            results["missing_init_docstring"].append(
                                f"{fname}:{node.name}.__init__"
                            )

                        # Return type annotation (public methods, not __init__)
                        if (
                            not item.name.startswith("_")
                            and item.name != "diagnostics"
                            and item.returns is None
                        ):
                            results["missing_return_type"].append(
                                f"{fname}:{node.name}.{item.name}"
                            )

                        # Empty methods (just pass or Ellipsis after docstring)
                        real_body = [
                            s for s in item.body
                            if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str))
                        ]
                        if len(real_body) == 1 and isinstance(real_body[0], ast.Pass):
                            if item.name != "__init__" and not item.name.startswith("_"):
                                # Exclude Exception classes
                                is_exc = any(
                                    isinstance(b, ast.Name) and b.id in ("Exception", "BaseException", "RuntimeError", "ValueError")
                                    for b in node.bases
                                )
                                if not is_exc:
                                    results["empty_methods"].append(
                                        f"{fname}:{node.name}.{item.name}"
                                    )

            # Bare except check
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                # Find which file this is in
                results["bare_except"].append(fname)

    return total, results


def scan_batch_infrastructure():
    """Scan for missing batch integration tests and diagnostics."""
    missing_tests = []
    missing_diags = []

    for batch_num in range(11, 32):  # Semester 8 = Batch 11-31
        test_file = f"sem8_batch{batch_num}_integration_tests.py"
        diag_file = f"sem8_batch{batch_num}_diagnostics.py"

        if not os.path.exists(os.path.join(ENGINE_DIR, test_file)):
            missing_tests.append(test_file)
        if not os.path.exists(os.path.join(ENGINE_DIR, diag_file)):
            missing_diags.append(diag_file)

    return missing_tests, missing_diags


def main():
    """Execute deep compliance scan."""
    total, results = scan_engines()
    missing_tests, missing_diags = scan_batch_infrastructure()

    print("=" * 70)
    print("OMNI SEMESTER 8 DEEP SCAN LEVEL 2")
    print("FULL CODE RULE 001-005 COMPLIANCE REPORT")
    print("=" * 70)
    print(f"Total engine files scanned: {total}")
    print()

    # Severity classification
    severity_map = {
        "syntax_error": "CRITICAL",
        "hardcoded_creds": "CRITICAL",
        "bare_except": "HIGH",
        "empty_methods": "HIGH",
        "todo_fixme": "HIGH",
        "missing_version": "MEDIUM",
        "missing_init_docstring": "MEDIUM",
        "missing_return_type": "LOW",
    }

    grand_total = 0
    for category in [
        "syntax_error",
        "hardcoded_creds",
        "bare_except",
        "empty_methods",
        "todo_fixme",
        "missing_version",
        "missing_init_docstring",
        "missing_return_type",
    ]:
        items = results[category]
        # Deduplicate bare_except per file
        if category == "bare_except":
            items = list(set(items))
        count = len(items)
        grand_total += count
        sev = severity_map[category]
        print(f"  [{sev:8s}] {category:30s}: {count}")

    # Batch infrastructure
    print()
    print(f"  [HIGH    ] missing_integration_tests     : {len(missing_tests)}")
    print(f"  [HIGH    ] missing_batch_diagnostics     : {len(missing_diags)}")
    grand_total += len(missing_tests) + len(missing_diags)

    print(f"\n  {'─' * 50}")
    print(f"  GRAND TOTAL DEFICIENCIES: {grand_total}")
    print("=" * 70)

    # Print details for critical/high items
    for category in ["syntax_error", "hardcoded_creds", "bare_except", "empty_methods", "todo_fixme"]:
        items = results[category]
        if category == "bare_except":
            items = list(set(items))
        if items:
            print(f"\n  === {category.upper()} ({len(items)}) ===")
            for item in items[:30]:
                print(f"    {item}")
            if len(items) > 30:
                print(f"    ... and {len(items) - 30} more")

    if missing_tests:
        print(f"\n  === MISSING INTEGRATION TESTS ({len(missing_tests)}) ===")
        for t in missing_tests:
            print(f"    {t}")

    if missing_diags:
        print(f"\n  === MISSING BATCH DIAGNOSTICS ({len(missing_diags)}) ===")
        for d in missing_diags:
            print(f"    {d}")

    # Print missing_version sample
    mv = results["missing_version"]
    if mv:
        print(f"\n  === MISSING ENGINE_VERSION ({len(mv)}) ===")
        for v in mv[:20]:
            print(f"    {v}")
        if len(mv) > 20:
            print(f"    ... and {len(mv) - 20} more")

    return 0


if __name__ == "__main__":
    sys.exit(main())
