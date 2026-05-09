# moe_longshu_gamedev_expert.py — Compute
# Layer: Compute — Game Development Large Language Model Router
# Inspired by: LongShuGameDev (A Game Development LLM)

import re

class LongShuGameDevExpert:
    """
    Validates and processes prompts specifically targeting Unity/Unreal Engine C++/C# code.
    Rejects general prompts to conserve MoE capacity.
    """
    def __init__(self):
        self.game_dev_keywords = re.compile(
            r"(monobehaviour|uobject|actor|rigidbody|unreal engine|unity3d|godot|gdscript|raycast)",
            re.IGNORECASE
        )

    def analyze_prompt(self, prompt: str) -> dict:
        """
        Determines if the prompt is relevant to Game Development.
        Returns the specific engine target if found.
        """
        is_gamedev = bool(self.game_dev_keywords.search(prompt))
        
        if not is_gamedev:
            return {"accepted": False, "reason": "Not a GameDev query"}

        target_engine = "Unknown"
        if "unity" in prompt.lower() or "monobehaviour" in prompt.lower():
            target_engine = "Unity C#"
        elif "unreal" in prompt.lower() or "uobject" in prompt.lower():
            target_engine = "Unreal C++"
        elif "godot" in prompt.lower():
            target_engine = "Godot GDScript"

        return {
            "accepted": True,
            "target_engine": target_engine,
            "routing_priority": 1.0 if target_engine != "Unknown" else 0.5
        }
