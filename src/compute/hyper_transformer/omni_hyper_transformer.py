# @omni-layer Compute | @omni-lang Python | @omni-batch 18 | @omni-semester 16
# @omni-repo wgcban/HyperTransformer
# @omni-description HyperTransformer: generates weights for task-specific
# adapters using a hypernetwork, enabling few-shot learning without fine-tuning.

import math
from typing import Dict, List, Tuple

class HyperNetwork:
    """Generates adapter weights from task embeddings."""
    def __init__(self, task_dim: int = 256, hidden_dim: int = 512, adapter_dim: int = 64):
        self.task_dim = task_dim
        self.hidden_dim = hidden_dim
        self.adapter_dim = adapter_dim
        self.w1 = [[math.sin(i*0.01+j*0.001)*0.02 for j in range(hidden_dim)] for i in range(task_dim)]
        self.w2 = [[math.cos(i*0.01+j*0.001)*0.02 for j in range(adapter_dim*adapter_dim)] for i in range(hidden_dim)]

    def generate_adapter(self, task_embedding: List[float]) -> List[List[float]]:
        hidden = [max(0, sum(task_embedding[i]*self.w1[i][h] for i in range(min(len(task_embedding), self.task_dim))))
                  for h in range(self.hidden_dim)]
        flat = [sum(hidden[h]*self.w2[h][o] for h in range(self.hidden_dim))
                for o in range(self.adapter_dim*self.adapter_dim)]
        adapter = []
        for i in range(self.adapter_dim):
            row = flat[i*self.adapter_dim:(i+1)*self.adapter_dim]
            norm = math.sqrt(sum(v*v for v in row))+1e-10
            adapter.append([v/norm*0.01 for v in row])
        return adapter

class TaskEncoder:
    """Encodes support set into a task embedding."""
    def __init__(self, d_model: int = 256):
        self.d = d_model

    def encode_support_set(self, examples: List[Tuple[List[float], int]]) -> List[float]:
        if not examples:
            return [0.0]*self.d
        emb = [0.0]*self.d
        for features, label in examples:
            for d in range(min(len(features), self.d)):
                emb[d] += features[d] * (1 + label * 0.1)
        n = len(examples)
        return [e/n for e in emb]

class HyperTransformer:
    """Few-shot learning via hypernetwork-generated adapters."""
    def __init__(self, d_model: int = 256, n_classes: int = 5):
        self.d_model = d_model
        self.n_classes = n_classes
        self.task_encoder = TaskEncoder(d_model)
        self.hyper = HyperNetwork(task_dim=d_model, adapter_dim=d_model)
        self.base_weights = [[math.sin(i*0.01+j*0.001)*0.1 for j in range(d_model)] for i in range(d_model)]

    def few_shot_classify(self, support: List[Tuple[List[float], int]], query: List[float]) -> List[float]:
        task_emb = self.task_encoder.encode_support_set(support)
        adapter = self.hyper.generate_adapter(task_emb)
        adapted = [[self.base_weights[i][j]+adapter[i%len(adapter)][j%len(adapter[0])]
                    for j in range(self.d_model)] for i in range(self.d_model)]
        hidden = [max(0, sum(query[j]*adapted[j][d] for j in range(min(len(query), self.d_model))))
                  for d in range(self.d_model)]
        logits = [sum(hidden[d]*math.sin((c+1)*(d+1)*0.001) for d in range(min(32, self.d_model)))
                  for c in range(self.n_classes)]
        mx = max(logits)
        exps = [math.exp(l-mx) for l in logits]
        sm = sum(exps)+1e-10
        return [e/sm for e in exps]

    def meta_train_step(self, tasks: List[Dict]) -> float:
        total_loss = 0.0
        for task in tasks:
            support = task.get("support", [])
            queries = task.get("queries", [])
            for q_feat, q_label in queries:
                probs = self.few_shot_classify(support, q_feat)
                loss = -math.log(max(probs[q_label % len(probs)], 1e-10))
                total_loss += loss
        return total_loss / max(len(tasks), 1)
