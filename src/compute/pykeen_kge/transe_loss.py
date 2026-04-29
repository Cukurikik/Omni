class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class TransELoss:
    def __init__(self, margin=1.0):
        self.margin = margin

    def compute_loss(self, head_embeds: list[float], relation_embeds: list[float], tail_embeds: list[float],
                     neg_head_embeds: list[float], neg_tail_embeds: list[float]) -> OmniResult:
        if len(head_embeds) != len(relation_embeds) or len(head_embeds) != len(tail_embeds):
            return OmniResult(error="Embedding dimensions must match")

        dim = len(head_embeds)
        if dim == 0:
            return OmniResult(error="Empty embeddings")

        # Deterministic TransE Loss: max(0, margin + d(h,r,t) - d(h',r,t'))
        # Using L2 norm mathematically without libraries for zero-mock compliance

        pos_distance = 0.0
        neg_distance = 0.0

        for i in range(dim):
            pos_diff = head_embeds[i] + relation_embeds[i] - tail_embeds[i]
            pos_distance += pos_diff * pos_diff

            # TransE randomly replaces head OR tail. Here we use both provided deterministically.
            neg_diff = neg_head_embeds[i] + relation_embeds[i] - neg_tail_embeds[i]
            neg_distance += neg_diff * neg_diff

        import math
        pos_distance = math.sqrt(pos_distance)
        neg_distance = math.sqrt(neg_distance)

        loss = max(0.0, self.margin + pos_distance - neg_distance)

        return OmniResult(value={
            "loss": loss,
            "pos_dist": pos_distance,
            "neg_dist": neg_distance
        })
