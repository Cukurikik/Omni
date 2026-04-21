# -*- coding: utf-8 -*-
"""Deep audit script for all OMNI engine files in Semester 7."""
import os
import ast
import sys

engine_dir = os.path.join("src", "compute", "python_core", "system")
issues = []
engine_count = 0

for fname in sorted(os.listdir(engine_dir)):
    if not fname.startswith("omni_") or not fname.endswith("_engine.py"):
        continue
    engine_count += 1
    fpath = os.path.join(engine_dir, fname)
    size = os.path.getsize(fpath)

    try:
        with open(fpath, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
    except SyntaxError as e:
        issues.append("SYNTAX_ERROR: {} -> {}".format(fname, e))
        continue

    # Only check TOP-LEVEL classes (direct children of module), not nested
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    if not classes:
        issues.append("NO_CLASS: {}".format(fname))
        continue

    for cls in classes:
        # Check class docstring
        has_doc = (
            cls.body
            and isinstance(cls.body[0], ast.Expr)
            and isinstance(cls.body[0].value, (ast.Str, ast.Constant))
        )
        if not has_doc:
            issues.append("NO_CLASS_DOCSTRING: {}::{}".format(fname, cls.name))

        # Check diagnostics method exists
        methods = [
            n.name
            for n in cls.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        if "diagnostics" not in methods:
            issues.append("NO_DIAGNOSTICS: {}::{}".format(fname, cls.name))

        # Check all methods have docstrings
        for node in cls.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                meth_has_doc = (
                    node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, (ast.Str, ast.Constant))
                )
                if not meth_has_doc:
                    issues.append(
                        "NO_METHOD_DOCSTRING: {}::{}.{}".format(
                            fname, cls.name, node.name
                        )
                    )

    if size < 1500:
        issues.append("TOO_SMALL ({}B): {}".format(size, fname))

# Check for missing diagnostics batch files (global batches 31-61 = S7 batches 1-31)
diag_dir = os.path.join("src", "compute", "python_core")
missing_diags = []
for gb in range(31, 62):
    dname = "batch{}_diagnostics.py".format(gb)
    if not os.path.exists(os.path.join(diag_dir, dname)):
        missing_diags.append(dname)

# Check for missing test files (S7 batches 1-31)
test_dir = "tests"
missing_tests = []
for sb in range(1, 32):
    tname = "test_batch{}_s7.py".format(sb)
    if not os.path.exists(os.path.join(test_dir, tname)):
        missing_tests.append(tname)

print("=" * 70)
print("  OMNI SEMESTER 7 DEEP AUDIT REPORT")
print("=" * 70)
print("")
print("Total engine files scanned: {}".format(engine_count))
print("Total deficiencies found : {}".format(len(issues)))
print("")

if issues:
    for i in issues:
        print("  [!!] {}".format(i))
else:
    print("  [OK] No engine deficiencies found.")

print("")
print("Missing diagnostics files: {}".format(len(missing_diags)))
for md in missing_diags:
    print("  [!!] MISSING: {}".format(md))

print("")
print("Missing test files: {}".format(len(missing_tests)))
for mt in missing_tests:
    print("  [!!] MISSING: {}".format(mt))

print("")
print("=" * 70)
total_issues = len(issues) + len(missing_diags) + len(missing_tests)
if total_issues == 0:
    print("  [OK] ZERO DEFICIENCIES -- SEMESTER 7 FULLY COMPLIANT")
else:
    print("  [!!] {} TOTAL DEFICIENCIES REQUIRE REMEDIATION".format(total_issues))
print("=" * 70)

sys.exit(0 if total_issues == 0 else 1)
