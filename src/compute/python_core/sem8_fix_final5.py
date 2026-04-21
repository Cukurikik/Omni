"""Fix the last 5 HIGH severity items."""
import os
import ast
import re

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))


def fix_dl_pytorch():
    """Fix LossFunctions missing class docstring."""
    fp = os.path.join(ENGINE_DIR, "omni_dl_pytorch_engine.py")
    with open(fp, "r", encoding="utf-8") as f:
        src = f.read()

    tree = ast.parse(src)
    lines = src.split("\n")

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "LossFunctions":
            # Check existing docstring
            if node.body and isinstance(node.body[0], ast.Expr):
                val = node.body[0].value
                if isinstance(val, ast.Constant) and isinstance(val.value, str):
                    print("  LossFunctions already has docstring")
                    return

            body_line = node.body[0].lineno - 1
            indent = "    "
            lines.insert(body_line, indent + '"""Production-grade loss function implementations."""')
            break

    new_src = "\n".join(lines)
    ast.parse(new_src)  # Verify
    with open(fp, "w", encoding="utf-8") as f:
        f.write(new_src)
    print("  [FIXED] omni_dl_pytorch_engine.py: LossFunctions docstring")


def fix_fastai_callbacks():
    """Fix 4 callback method docstrings."""
    fp = os.path.join(ENGINE_DIR, "omni_fastai_course_engine.py")
    with open(fp, "r", encoding="utf-8") as f:
        src = f.read()

    tree = ast.parse(src)
    lines = src.split("\n")
    insertions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "OmniCallback":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name.startswith("on_"):
                    # Check docstring
                    has_doc = False
                    if item.body and isinstance(item.body[0], ast.Expr):
                        v = item.body[0].value
                        if isinstance(v, ast.Constant) and isinstance(v.value, str):
                            has_doc = True
                    if not has_doc:
                        body_line = item.body[0].lineno - 1
                        match = re.match(r'^(\s*)', lines[body_line])
                        indent = match.group(1) if match else "        "
                        name = item.name.replace("_", " ")
                        insertions.append(
                            (body_line, f'{indent}"""Handle {name} callback event."""')
                        )

    insertions.sort(key=lambda x: x[0], reverse=True)
    for ln, txt in insertions:
        lines.insert(ln, txt)

    new_src = "\n".join(lines)
    ast.parse(new_src)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(new_src)
    print(f"  [FIXED] omni_fastai_course_engine.py: {len(insertions)} callback docstrings")


if __name__ == "__main__":
    print("Fixing last 5 HIGH items...")
    fix_dl_pytorch()
    fix_fastai_callbacks()
    print("Done.")
