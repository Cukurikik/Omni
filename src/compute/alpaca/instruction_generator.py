from typing import List, Dict, Optional, Tuple
import re

# OMNI STANFORD ALPACA: Self-Instruct Generator Pipeline
# Python logic mapping the generation of instruction-response pairs via an LLM.
# Source: tatsu-lab/stanford_alpaca

class AlpacaGeneratorError(Exception):
    pass

class InstructionGenerator:
    """
    Generates synthetic instruction data using a strong teacher model.
    Based on the Self-Instruct paper methodology.
    """
    def __init__(self, llm_client):
        """
        llm_client: A mock object representing an API client to OpenAI or a local strong model.
        """
        self.llm = llm_client
        self.system_prompt = (
            "You are asked to come up with a set of 5 diverse task instructions. "
            "These task instructions will be given to a GPT model and we will evaluate the GPT model for completing the instructions. "
            "Here are the requirements:\n"
            "1. Try not to repeat the verb for each instruction.\n"
            "2. The language used should be diverse.\n"
            "3. The type of instructions should be diverse (e.g. brainstorming, classification, editing).\n"
        )

    def parse_generations(self, text: str) -> List[str]:
        """
        Parses the raw text output from the LLM into a list of instructions.
        Assumes output format like "1. [Instruction 1]\n2. [Instruction 2]"
        """
        instructions = []
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            # Regex to match "1. " or "1) " at start of line
            match = re.match(r'^\d+[\.\)]\s*(.*)', line)
            if match:
                instructions.append(match.group(1))
        return instructions

    def generate_seed_tasks(self, num_tasks: int = 5) -> Tuple[Optional[List[str]], Optional[AlpacaGeneratorError]]:
        try:
            # Simulate LLM call
            prompt = self.system_prompt + f"\nPlease generate {num_tasks} instructions now:\n"
            
            # In a real scenario, this is an async network call
            raw_output = self.llm.generate(prompt)
            
            instructions = self.parse_generations(raw_output)
            
            if not instructions:
                return None, AlpacaGeneratorError("Failed to parse any instructions from LLM output.")
                
            return instructions[:num_tasks], None
            
        except Exception as e:
            return None, AlpacaGeneratorError(f"Instruction generation failed: {str(e)}")

class MockLLMClient:
    def generate(self, prompt: str) -> str:
        return """1. Write a short poem about a mechanical keyboard.
2. Classify the following sentiment as positive or negative: "I abhor this weather."
3. Translate the phrase "Hello World" into French.
4. Suggest three ways to improve a website's SEO.
5. Summarize the plot of The Matrix in one sentence."""
