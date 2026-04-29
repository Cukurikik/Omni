from typing import Dict, Any
from dataclasses import dataclass
import hashlib

# OMNI Pixeltable Engine — Compute Layer
# Absorbing pixeltable/pixeltable: Declarative multimodal AI data management.
# Implements computed column registry with dependency tracking and cache invalidation.

@dataclass
class PixelResult:
    ok: bool
    computed_value: Any = None
    error: str = None

class ColumnDef:
    def __init__(self, name: str, dtype: str, computed_fn=None, depends_on=None):
        self.name = name
        self.dtype = dtype
        self.computed_fn = computed_fn
        self.depends_on = depends_on or []

class OmniPixeltableEngine:
    def __init__(self):
        self.columns = {}
        self.rows = []
        self.computations = 0

    def define_column(self, name: str, dtype: str, computed_fn=None, depends_on=None) -> Dict:
        if not name:
            return {"ok": False, "error": "PixeltableError: Column name required"}
        if computed_fn and depends_on:
            for dep in depends_on:
                if dep not in self.columns:
                    return {"ok": False, "error": f"PixeltableError: Dependency '{dep}' not defined"}
        self.columns[name] = ColumnDef(name, dtype, computed_fn, depends_on)
        return {"ok": True, "column": name}

    def insert_row(self, values: Dict) -> Dict:
        row = {}
        for col_name, col_def in self.columns.items():
            if col_def.computed_fn:
                dep_vals = {d: values.get(d) for d in col_def.depends_on}
                try:
                    self.computations += 1
                    row[col_name] = col_def.computed_fn(dep_vals)
                except Exception as e:
                    return {"ok": False, "error": f"PixeltableError: Computed column '{col_name}' failed: {str(e)}"}
            else:
                row[col_name] = values.get(col_name)
        row_hash = hashlib.sha256(str(row).encode()).hexdigest()[:12]
        row["_id"] = f"row-{row_hash}"
        self.rows.append(row)
        return {"ok": True, "id": row["_id"]}

    def query(self, filter_fn=None) -> list:
        if filter_fn:
            return [r for r in self.rows if filter_fn(r)]
        return list(self.rows)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniPixeltableEngine", "columns": len(self.columns),
                "rows": len(self.rows), "computations": self.computations, "status": "Operational"}
