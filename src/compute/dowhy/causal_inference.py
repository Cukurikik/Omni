import numpy as np

class DoWhyCausalModel:
    def __init__(self, treatment, outcome, confounders):
        self.treatment = treatment
        self.outcome = outcome
        self.confounders = confounders

    def estimate_ate(self, data):
        # Propensity score matching stub
        t = data[self.treatment]
        y = data[self.outcome]
        c = data[self.confounders]
        
        # Simple difference in means
        treated = y[t == 1]
        control = y[t == 0]
        
        return np.mean(treated) - np.mean(control)

if __name__ == "__main__":
    import pandas as pd
    data = pd.DataFrame({'t': [1,0,1,0], 'y': [10,5,12,4], 'c': [1,1,0,0]})
    model = DoWhyCausalModel('t', 'y', ['c'])
    print(f"ATE: {model.estimate_ate(data)}")
