from typing import List, Dict
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniNovfensecKvdeveloperEngine:
    """
    OmniNovfensecKvdeveloperEngine
    
    Level-2 Abstraction for Cross-platform Kivy app scaffolding (assimilated from 'Novfensec/KvDeveloper').
    Provides mathematically sound structural validation for Python cross-platform project 
    initialization architectures to ensure core build dependencies exist before compiler execution.
    """

    REQUIRED_SCAFFOLDING_TEMPLATES = {
        "kivy_standard": ["main.py", "app.kv", "requirements.txt", ".gitignore", "buildozer.spec"],
        "kivymd_standard": ["main.py", "theme.json", "requirements.txt", "buildozer.spec"],
        "python_minimum": ["main.py", "requirements.txt"]
    }

    @classmethod
    def validate_scaffolding_architecture(cls, template_type: str, generated_files: List[str]) -> Result[bool, Exception]:
        """
        Checks the set difference between expected template files and generated files 
        to ensure zero-loss infrastructure generation via CLI.
        
        Args:
            template_type: The archetype blueprint identifier.
            generated_files: List of file components resolved by the CLI engine.
            
        Returns:
            Result[bool, Exception]: Ok if set difference <= zero (all required files present),
            Err if architecture is structurally incomplete.
        """
        if template_type not in cls.REQUIRED_SCAFFOLDING_TEMPLATES:
            return Err(Exception(f"Unknown archetype: '{template_type}'. Valid configurations: {list(cls.REQUIRED_SCAFFOLDING_TEMPLATES.keys())}"))
            
        required_set = set(cls.REQUIRED_SCAFFOLDING_TEMPLATES[template_type])
        generated_set = set(generated_files)
        
        missing = required_set - generated_set
        if missing:
            return Err(Exception(f"Scaffolding Infrastructure Failure. Missing architectural pillars: {list(missing)}"))
            
        return Ok(True)

    @classmethod
    def diagnostics(cls) -> Dict[str, str]:
        return {
            "status": "operational",
            "mode": "Zero-Prod Set Theory Validation",
            "layer": "System/Build",
            "rule": "Strict Archetype Subsets"
        }
