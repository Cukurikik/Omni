# Omni REFLECT Robot Failure Analyzer
# Ref: real-stanford/reflect — CoRL 2023, MIT
from typing import List, Dict

def summarize_experience(actions: List[Dict], success: bool) -> Dict:
    return {"n_actions": len(actions), "success": success,
            "action_sequence": [a.get("type", "unknown") for a in actions],
            "failure_point": None if success else actions[-1] if actions else None}

def explain_failure(experience: Dict) -> str:
    if experience.get("success"): return "Task completed successfully."
    fp = experience.get("failure_point", {})
    return f"Failure at action '{fp.get('type', 'unknown')}': likely cause is {fp.get('error', 'unspecified')}"

def suggest_correction(failure_type: str) -> List[str]:
    corrections = {
        "grasp_fail": ["Adjust gripper force", "Re-estimate object pose", "Try different grasp point"],
        "navigation_fail": ["Replan path", "Check for obstacles", "Reduce speed"],
        "perception_fail": ["Increase camera exposure", "Move closer to object", "Switch to depth sensor"],
    }
    return corrections.get(failure_type, ["Retry with different parameters"])

def hierarchical_summary(episodes: List[Dict]) -> Dict:
    successes = sum(1 for e in episodes if e.get("success"))
    common_failures = {}
    for e in episodes:
        if not e.get("success"):
            ft = e.get("failure_point", {}).get("type", "unknown")
            common_failures[ft] = common_failures.get(ft, 0) + 1
    return {"total": len(episodes), "success_rate": round(successes / max(len(episodes), 1), 4),
            "common_failures": common_failures}
