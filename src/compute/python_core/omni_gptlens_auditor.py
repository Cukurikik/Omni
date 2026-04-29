# Omni GPTLens Smart Contract Auditor
# Ref: git-disl/GPTLens — TPS'23
# Implements: Auditor-Critic adversarial pipeline, vulnerability pattern detection
import re
from typing import List, Dict

VULN_PATTERNS = {
    "reentrancy": r'\.call\{value:.*\}\(""?\)',
    "unchecked_return": r'\.send\(|\.transfer\(',
    "integer_overflow": r'\+\+|--|\+=|-=',
    "tx_origin": r'tx\.origin',
    "delegatecall": r'\.delegatecall\(',
    "selfdestruct": r'selfdestruct\(|suicide\(',
}

def auditor_scan(source_code: str) -> List[Dict]:
    findings = []
    lines = source_code.split('\n')
    for i, line in enumerate(lines):
        for vuln_type, pattern in VULN_PATTERNS.items():
            if re.search(pattern, line):
                findings.append({"line": i + 1, "type": vuln_type,
                                 "snippet": line.strip()[:80], "severity": "medium"})
    return findings

def critic_evaluate(findings: List[Dict], source_code: str) -> List[Dict]:
    verified = []
    for f in findings:
        confidence = 0.5
        if f["type"] == "reentrancy" and "nonReentrant" not in source_code:
            confidence = 0.9
        elif f["type"] == "tx_origin":
            confidence = 0.85
        elif f["type"] == "delegatecall":
            confidence = 0.8
        f["critic_confidence"] = round(confidence, 4)
        f["verified"] = confidence > 0.6
        if f["verified"]:
            verified.append(f)
    return verified

def gptlens_pipeline(source_code: str) -> Dict:
    raw = auditor_scan(source_code)
    verified = critic_evaluate(raw, source_code)
    return {"total_flagged": len(raw), "verified_vulnerabilities": len(verified),
            "false_positive_rate": round(1 - len(verified) / max(len(raw), 1), 4),
            "findings": verified}
