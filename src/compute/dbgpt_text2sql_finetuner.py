# OMNI Compute Layer - DB-GPT Text2SQL Finetuner
class DBGPTError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def format_spider_dataset_instruction(db_schema: str, question: str) -> Result:
    """Formats Text2SQL prompt adhering to DB-GPT SFT guidelines."""
    try:
        if not db_schema or not question:
            return Result(error=DBGPTError("Missing schema or question"))
            
        instruction = f"Given the following database schema:\n{db_schema}\nAnswer the question with an SQL query:\n{question}"
        
        return Result(value={"instruction": instruction})
    except Exception as e:
        return Result(error=DBGPTError(f"Formatting failed: {str(e)}"))
