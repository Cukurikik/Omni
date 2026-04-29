import numpy as np

class OrangeDataTable:
    """
    OMNI Engine: Orange3 core Data Table structure.
    Handles domain translation and numpy backing.
    """
    def __init__(self, X: np.ndarray, Y: np.ndarray, domain_attributes: list):
        self.X = X
        self.Y = Y
        self.domain = domain_attributes

    def select_rows(self, indices: list):
        """Zero-copy view if possible, otherwise slice."""
        return OrangeDataTable(self.X[indices], self.Y[indices], self.domain)

    def select_columns(self, attr_indices: list):
        new_domain = [self.domain[i] for i in attr_indices]
        return OrangeDataTable(self.X[:, attr_indices], self.Y, new_domain)

    def discretize(self, bins=4):
        """Example computation operation"""
        discretized_X = np.zeros_like(self.X)
        for col in range(self.X.shape[1]):
            # Simple equal-width binning
            col_data = self.X[:, col]
            discretized_X[:, col] = np.digitize(col_data, np.histogram(col_data, bins=bins)[1])
        return OrangeDataTable(discretized_X, self.Y, self.domain)
