class OmniCoEdITTuner:
    """OMNI Compute Layer: CoEdIT Task Formatter (Zero-Mock)"""
    
    def __init__(self, tasks: list[str]):
        self.tasks = tasks

    def format_instruction(self, text: str, task_id: str) -> str:
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} is not supported.")
            
        if task_id == "gec":
            return f"Fix grammatical errors in this text: {text}"
        elif task_id == "simplification":
            return f"Make this text simpler to read: {text}"
        elif task_id == "paraphrase":
            return f"Paraphrase this sentence: {text}"
            
        return f"Edit this text: {text}"
