from typing import List, Dict

class OmniChatFormatter:
    """
    OMNI Framework - Chat Template Formatter
    Prepares raw conversational arrays into the exact string format required
    by the MoE model (e.g., Llama-3, ChatML, or DeepSeek specific formats)
    before tokenization.
    """
    def __init__(self, template_type: str = "chatml"):
        self.template_type = template_type
        print(f"OMNI Python: Chat Formatter initialized using '{template_type}' template.")

    def apply_template(self, messages: List[Dict[str, str]]) -> str:
        """
        messages: [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
        """
        formatted_prompt = ""

        if self.template_type == "chatml":
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                formatted_prompt += f"<|im_start|>{role}\n{content}<|im_end|>\n"
            
            # Append the assistant trigger
            formatted_prompt += "<|im_start|>assistant\n"
            
        elif self.template_type == "deepseek":
            # DeepSeek specific instruction format
            for msg in messages:
                if msg["role"] == "system":
                    formatted_prompt += f"{msg['content']}\n\n"
                elif msg["role"] == "user":
                    formatted_prompt += f"User: {msg['content']}\n\n"
                elif msg["role"] == "assistant":
                    formatted_prompt += f"Assistant: {msg['content']}\n\n"
            formatted_prompt += "Assistant:"
            
        else:
            raise ValueError("Unknown template type")

        return formatted_prompt

# Usage
# formatter = OmniChatFormatter("chatml")
# msgs = [{"role": "system", "content": "You are OMNI."}, {"role": "user", "content": "Hi!"}]
# print(formatter.apply_template(msgs))
