# moe_bayesian_lora_cluster.py — Compute
# Layer: Compute — Bayesian Clustering for Continual LoRA Learning
# Inspired by: xctopus-core (Bayesian clustering, Catastrophic Forgetting)

import numpy as np
from sklearn.mixture import BayesianGaussianMixture

class BayesianLoRACluster:
    """
    Groups dynamic LoRA adapters into Bayesian clusters based on input embeddings 
    to prevent catastrophic forgetting.
    """
    def __init__(self, max_components: int = 10):
        self.max_components = max_components
        self.bgm = BayesianGaussianMixture(
            n_components=max_components,
            covariance_type='full',
            weight_concentration_prior_type='dirichlet_process',
            random_state=42
        )
        self.is_fitted = False
        self.lora_registry = {}

    def fit_adapters(self, embeddings: np.ndarray, adapter_ids: list[str]):
        """ Fits the BGM on the task embeddings and maps clusters to LoRA IDs. """
        self.bgm.fit(embeddings)
        cluster_assignments = self.bgm.predict(embeddings)
        
        for idx, cluster_id in enumerate(cluster_assignments):
            if cluster_id not in self.lora_registry:
                self.lora_registry[cluster_id] = []
            self.lora_registry[cluster_id].append(adapter_ids[idx])
            
        self.is_fitted = True

    def route_to_adapters(self, query_embedding: np.ndarray) -> list[str]:
        """ Identifies the best LoRA adapters to activate based on posterior probability. """
        if not self.is_fitted:
            raise RuntimeError("Bayesian cluster not fitted yet.")
            
        probs = self.bgm.predict_proba(query_embedding.reshape(1, -1))[0]
        best_cluster = np.argmax(probs)
        
        if probs[best_cluster] < 0.1:
            return [] # Unseen domain, fallback to base model
            
        return self.lora_registry.get(best_cluster, [])
