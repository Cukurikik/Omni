from omni.core import Result, Ok, Err

def run_mistral_pipeline(doc_store: list) -> Result[bool, Exception]:
    if not doc_store:
        return Err(ValueError("Empty document store"))
    return Ok(True)
