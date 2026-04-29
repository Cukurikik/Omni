import numpy as np

class SurpriseSVD:
    def __init__(self, n_factors=100, n_epochs=20, lr=0.005, reg=0.02):
        self.n_factors = n_factors
        self.n_epochs = n_epochs
        self.lr = lr
        self.reg = reg
        
    def fit(self, trainset):
        self.pu = np.random.normal(0, 0.1, (trainset.n_users, self.n_factors))
        self.qi = np.random.normal(0, 0.1, (trainset.n_items, self.n_factors))
        self.bu = np.zeros(trainset.n_users)
        self.bi = np.zeros(trainset.n_items)
        self.global_mean = trainset.global_mean
        
        for _ in range(self.n_epochs):
            for u, i, r in trainset.all_ratings():
                err = r - self.predict(u, i)
                self.bu[u] += self.lr * (err - self.reg * self.bu[u])
                self.bi[i] += self.lr * (err - self.reg * self.bi[i])
                pu_u = self.pu[u].copy()
                self.pu[u] += self.lr * (err * self.qi[i] - self.reg * self.pu[u])
                self.qi[i] += self.lr * (err * pu_u - self.reg * self.qi[i])
                
    def predict(self, u, i):
        return self.global_mean + self.bu[u] + self.bi[i] + np.dot(self.pu[u], self.qi[i])
