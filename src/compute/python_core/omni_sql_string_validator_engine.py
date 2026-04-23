"""OmniSqlStringValidatorEngine for deterministic SQL syntax structural checking."""
from typing import Dict, Any, List
import re
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniSqlStringValidatorEngine(OmniBaseEngine):
    """Production-grade Omni Sql String Validator Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def validate(self, sql_query: str) -> Result[Dict[str, Any], str]:
        """
        Validates basic structure and flags dangerous keywords deterministically.
        This is a structural parser, not a full AST builder.
        """
        try:
            if not isinstance(sql_query, str):
                return Result.fail("SQL query must be a string")

            clean_query = sql_query.strip().upper()
            
            dangerous_keywords = ["DROP", "TRUNCATE", "ALTER", "GRANT", "REVOKE"]
            found_dangerous = []
            
            for word in clean_query.split():
                if word in dangerous_keywords:
                    found_dangerous.append(word)

            matched_structure = False
            
            # Simple regex for SELECT ... FROM ...
            # E.g., SELECT id, name FROM users;
            select_pattern = re.compile(r"^SELECT\s+(.+)\s+FROM\s+([A-Z0-9_]+)(?:\s+WHERE\s+(.+))?;?$")
            match = select_pattern.match(clean_query)
            
            extracted_table = None
            extracted_columns = None
            extracted_where = None

            if match:
                matched_structure = True
                extracted_columns = [c.strip() for c in match.group(1).split(',')]
                extracted_table = match.group(2)
                if match.group(3):
                    extracted_where = match.group(3).strip()
                    if extracted_where.endswith(';'):
                        extracted_where = extracted_where[:-1].strip()

            return Result.ok({
                "is_valid_structure": matched_structure,
                "is_safe": len(found_dangerous) == 0,
                "dangerous_keywords_found": found_dangerous,
                "table": extracted_table,
                "columns": extracted_columns,
                "where_clause": extracted_where
            })
            
        except Exception as e:
            return Result.fail(str(e))

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniSqlStringValidatorEngine",
            "status": "operational",
            "complexity": "O(N)"
        }
