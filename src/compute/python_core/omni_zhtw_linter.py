# Omni ZHTW-MCP Linguistic Linter Engine
# Ref: sysprog21/zhtw-mcp — MIT | Traditional Chinese linting
import re
from typing import List, Dict

COMMON_ERRORS = {
    "的话": "的話", "并且": "並且", "学习": "學習", "计算": "計算",
    "软件": "軟體", "信息": "資訊", "视频": "影片", "网络": "網路",
}

def lint_text(text: str) -> List[Dict]:
    issues = []
    for simplified, traditional in COMMON_ERRORS.items():
        for m in re.finditer(re.escape(simplified), text):
            issues.append({"position": m.start(), "found": simplified, "suggestion": traditional, "rule": "zh-tw-conversion"})
    return issues

def apply_fixes(text: str, issues: List[Dict]) -> str:
    for issue in sorted(issues, key=lambda x: x["position"], reverse=True):
        text = text[:issue["position"]] + issue["suggestion"] + text[issue["position"]+len(issue["found"]):]
    return text

def lint_score(text: str) -> Dict:
    issues = lint_text(text)
    words = len(text)
    return {"n_issues": len(issues), "score": round(1 - len(issues)/max(words, 1), 4)}
