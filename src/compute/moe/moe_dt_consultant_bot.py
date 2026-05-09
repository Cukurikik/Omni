# moe_dt_consultant_bot.py — Compute Layer: DT Consultant Bot
# Python conversational logic executing structured interviews for digital transformations.

from typing import Dict, List, Any

class ConsultantBot:
    def __init__(self):
        self.current_state = "INIT"
        self.context: Dict[str, Any] = {}
        
    def analyze_response(self, user_input: str) -> str:
        """
        Processes text input to extract business intent using LLM inference patterns.
        """
        user_input = user_input.lower()
        
        if self.current_state == "INIT":
            self.current_state = "PAIN_POINTS"
            return "What are the primary operational bottlenecks your organization faces today?"
            
        elif self.current_state == "PAIN_POINTS":
            if "legacy" in user_input or "slow" in user_input:
                self.context["has_legacy_debt"] = True
            
            self.current_state = "BUDGET"
            return "Understood. Have you allocated a budget tier for this transformation?"
            
        elif self.current_state == "BUDGET":
            self.current_state = "COMPLETE"
            return "Thank you. I am generating your strategic blueprint now."
            
        return "The consultation is complete."

    def get_structured_data(self) -> Dict[str, Any]:
        return self.context
