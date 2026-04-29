# OMNI Compute Layer - DS2 Rating System
import numpy as np

class DS2Error(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def curate_data_by_rating(data_matrix: np.ndarray, rating_threshold: float) -> Result:
    """
    Implements Data Efficiency via Curating LLM-Driven Rating Systems.
    """
    try:
        if data_matrix.shape[1] < 2:
            return Result(error=DS2Error("Data matrix must have at least features and a rating column"))
            
        ratings = data_matrix[:, -1]
        valid_indices = np.where(ratings >= rating_threshold)[0]
        
        if len(valid_indices) == 0:
            return Result(error=DS2Error("No data meets the rating threshold"))
            
        curated_data = data_matrix[valid_indices]
        return Result(value=curated_data)
    except Exception as e:
        return Result(error=DS2Error(f"Curation failed: {str(e)}"))
