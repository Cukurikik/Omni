# OMNI Compute Layer - AI Academy Concept Extractor
class AcademyError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def extract_key_learning_objectives(notebook_cells: list) -> Result:
    """Extracts markdown headers from Jupyter Notebooks as learning objectives."""
    try:
        if not notebook_cells:
            return Result(error=AcademyError("Notebook is empty"))
            
        objectives = [cell["source"] for cell in notebook_cells if cell["cell_type"] == "markdown" and cell["source"].startswith("##")]
        
        return Result(value={"learning_objectives": objectives})
    except Exception as e:
        return Result(error=AcademyError(f"Extraction failed: {str(e)}"))
