import torch
from sklearn.base import BaseEstimator, ClassifierMixin

class NeuralNetClassifier(BaseEstimator, ClassifierMixin):
    """
    OMNI Engine: Skorch-style Scikit-Learn wrapper for PyTorch networks.
    """
    def __init__(self, module, criterion=torch.nn.CrossEntropyLoss, lr=0.01, max_epochs=10):
        self.module = module
        self.criterion = criterion()
        self.lr = lr
        self.max_epochs = max_epochs
        self.optimizer_ = None

    def fit(self, X, y):
        # X, y are numpy arrays
        X_t = torch.tensor(X, dtype=torch.float32)
        y_t = torch.tensor(y, dtype=torch.long)
        
        self.optimizer_ = torch.optim.Adam(self.module.parameters(), lr=self.lr)
        
        for epoch in range(self.max_epochs):
            self.optimizer_.zero_grad()
            y_pred = self.module(X_t)
            loss = self.criterion(y_pred, y_t)
            loss.backward()
            self.optimizer_.step()
            
        return self

    def predict(self, X):
        X_t = torch.tensor(X, dtype=torch.float32)
        with torch.no_grad():
            y_pred = self.module(X_t)
            return y_pred.argmax(dim=1).numpy()
