"""omni-webpack-killer â€” Data Transformation Engine"""
from typing import Any, Dict, List, Optional
import json, csv, io

class Transformer:
    @staticmethod
    def to_json(data: Any) -> str: return json.dumps(data, default=str)
    @staticmethod
    def from_json(raw: str) -> Any: return json.loads(raw)
    @staticmethod
    def to_csv(rows: List[Dict]) -> str:
        if not rows: return ""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader(); writer.writerows(rows)
        return output.getvalue()
    @staticmethod
    def flatten(nested: Dict, prefix: str = "") -> Dict:
        items = {}
        for k, v in nested.items():
            key = f'{prefix}.{k}' if prefix else k
            if isinstance(v, dict): items.update(Transformer.flatten(v, key))
            else: items[key] = v
        return items
    @staticmethod
    def group_by(items: List[Dict], key: str) -> Dict[str, List]:
        groups = {}
        for item in items:
            k = str(item.get(key, 'unknown'))
            groups.setdefault(k, []).append(item)
        return groups
    @staticmethod
    def filter_by(items: List[Dict], predicate) -> List[Dict]: return [i for i in items if predicate(i)]
    @staticmethod
    def map_values(items: List[Dict], fn) -> List: return [fn(i) for i in items]
    @staticmethod
    def reduce_values(items: List, fn, initial=None): 
        acc = initial
        for item in items: acc = fn(acc, item) if acc is not None else item
        return acc