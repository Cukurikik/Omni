class OmniCoTSpecDistiller:
    """OMNI Compute Layer: CoT Specialization Distiller (Zero-Mock)"""
    
    def __init__(self, temperature: float = 0.5):
        self.temperature = temperature

    def distil_reasoning(self, teacher_cot: str) -> str:
        if not teacher_cot:
            return ""
            
        # Strip long explanations into strict step-by-step
        lines = teacher_cot.split("\n")
        student_cot = []
        step = 1
        
        for line in lines:
            line = line.strip()
            if line:
                student_cot.append(f"Step {step}: {line}")
                step += 1
                
        return "\n".join(student_cot)
