import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

def parse_and_serialize_table(file_path: str) -> Tuple[str, Dict[str, Any]]:
    # Production table parser for LLMs
    try:
        df = pd.read_csv(file_path)
        markdown_repr = df.to_markdown()
        metadata = {
            "rows": len(df),
            "columns": len(df.columns),
            "col_types": df.dtypes.astype(str).to_dict()
        }
        return markdown_repr, metadata
    except Exception as e:
        raise RuntimeError(f"OmniError: Failed to parse table at {file_path}: {e}")
