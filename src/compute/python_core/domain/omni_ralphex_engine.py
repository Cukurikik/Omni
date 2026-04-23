ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI RALPHEX ENGINE
# ===========================================================================
# Source Paradigm: umputun/ralphex
# Domain Layer  : Domain (Business logic, pattern filtering & semantic rules)
# Zero-Prod     : 100% Native — re, json, datetime, sqlite3
# ===========================================================================
"""
Ralphex Engine processes high-volume log and feed data through 
compiled regex patterns, structuring chaotic strings into strongly-typed 
Domain models.
"""

import json
import os
import re
import sqlite3
import time
from typing import Dict, List, Any, Optional

def Ok(data: Any) -> Dict:
    return {"status": "ok", "error": None, "data": data}

def Err(reason: str) -> Dict:
    return {"status": "error", "error": reason, "data": None}


class RalphexRuleStore:
    """Manages parsing rules and symbolic expressions."""
    def __init__(self):
        self.db_path = os.path.join(os.getcwd(), ".omni_ralphex_rules.db")
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS rules (
                    rule_id TEXT PRIMARY KEY,
                    pattern TEXT,
                    target_domain TEXT,
                    created_at REAL
                )
            ''')
            conn.commit()
            
    def add_rule(self, rule_id: str, pattern: str, target_domain: str) -> Dict:
        try:
            # Validate regex compile before insertion
            re.compile(pattern)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    'INSERT OR REPLACE INTO rules VALUES (?, ?, ?, ?)',
                    (rule_id, pattern, target_domain, time.time())
                )
                conn.commit()
            return Ok({"rule_id": rule_id, "status": "active"})
        except re.error as e:
            return Err(f"Invalid regex pattern: {str(e)}")

    def get_all_rules(self) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute('SELECT * FROM rules').fetchall()
            return [dict(r) for r in rows]


class OmniRalphexEngine:
    """
    Evaluates incoming streams of text/logs against compiled Ralphex rules 
    to extract domain-specific schemas.
    """
    def __init__(self):
        self.store = RalphexRuleStore()
        
    def bootstrap_default_rules(self):
        """Seeds common log extraction rules."""
        self.store.add_rule("extract_ip", r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", "NetworkSecurity")
        self.store.add_rule("extract_email", r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "UserDomain")
        self.store.add_rule("extract_jwt", r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-\]+", "AuthDomain")

    def process_payload(self, text_payload: str) -> Dict:
        """Runs the payload through all active rules and routes matches."""
        rules = self.store.get_all_rules()
        results = {}
        
        for rule in rules:
            rid = rule["rule_id"]
            pattern = re.compile(rule["pattern"])
            matches = pattern.findall(text_payload)
            if matches:
                domain = rule["target_domain"]
                if domain not in results:
                    results[domain] = {}
                results[domain][rid] = list(set(matches)) # unique matches
                
        if not results:
            return Err("No rules matched the payload.")
            
        return Ok({
            "bytes_processed": len(text_payload),
            "domains_triggered": list(results.keys()),
            "extractions": results
        })

    def diagnostics(self) -> Dict:
        rules = self.store.get_all_rules()
        return {
            "engine": "OmniRalphexEngine",
            "status": "online",
            "active_patterns": len(rules),
            "capabilities": ["regex_pipeline", "domain_structuring", "symbolic_expression_parser"]
        }


if __name__ == "__main__":
    engine = OmniRalphexEngine()
    engine.bootstrap_default_rules()
    res = engine.process_payload("User admin@omniframework.local logged in from IP 192.168.1.5 with token eyJhbGciOiJIUzI1.eyJ1c2Vy.signature")
    print(json.dumps(res, indent=2))
    print(json.dumps(engine.diagnostics(), indent=2))
