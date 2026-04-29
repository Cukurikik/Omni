# OMNI Compute Layer - Axolotl Config Parser
import yaml

class AxolotlError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def parse_yaml_config(yaml_string: str) -> Result:
    """Parses and validates Axolotl fine-tuning YAML configurations."""
    try:
        if not yaml_string:
            return Result(error=AxolotlError("Empty YAML configuration"))
            
        config = yaml.safe_load(yaml_string)
        if "base_model" not in config:
            return Result(error=AxolotlError("base_model is required in Axolotl config"))
            
        return Result(value={"parsed_config": config})
    except Exception as e:
        return Result(error=AxolotlError(f"Config parse failed: {str(e)}"))
