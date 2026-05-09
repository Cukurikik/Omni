"""
omni_beam_search.py — Beam Search Decoding
Layer: Compute / AI

Implements an efficient Beam Search decoding algorithm for autoregressive 
language models, tracking log-probabilities and maintaining top-k sequences.
Zero-mock.
"""

import torch

class OmniBeamSearchNode:
    def __init__(self, sequence, log_prob, length):
        self.sequence = sequence  # Tensor of token IDs
        self.log_prob = log_prob  # Cumulative log probability
        self.length = length      # Length of the sequence

    def __lt__(self, other):
        # We want to keep the highest log probability
        # Normalizing by length prevents bias towards shorter sequences
        return (self.log_prob / self.length) < (other.log_prob / other.length)

class OmniBeamSearch:
    def __init__(self, beam_width: int, max_len: int, eos_token_id: int):
        self.beam_width = beam_width
        self.max_len = max_len
        self.eos_token_id = eos_token_id

    def decode(self, model, start_token_id: int, device: torch.device):
        """
        Executes beam search decoding using the provided generative model.
        Model should have a `forward_step(sequence)` method that returns 
        log_softmax probabilities for the next token.
        """
        initial_seq = torch.tensor([start_token_id], dtype=torch.long, device=device)
        start_node = OmniBeamSearchNode(sequence=initial_seq, log_prob=0.0, length=1)
        
        # Beams list sorted by score (highest first)
        beams = [start_node]
        finished_beams = []

        for step in range(self.max_len):
            all_candidates = []
            
            for node in beams:
                # If sequence ends, move to finished
                if node.sequence[-1].item() == self.eos_token_id:
                    finished_beams.append(node)
                    continue

                # Get next token log probabilities from model
                # shape: (VocabSize)
                with torch.no_grad():
                    log_probs = model.forward_step(node.sequence.unsqueeze(0)).squeeze(0)

                # Get top K tokens to expand this node
                topk_log_probs, topk_indices = torch.topk(log_probs, self.beam_width)

                for i in range(self.beam_width):
                    token_id = topk_indices[i].unsqueeze(0)
                    new_log_prob = node.log_prob + topk_log_probs[i].item()
                    new_seq = torch.cat([node.sequence, token_id])
                    
                    candidate = OmniBeamSearchNode(
                        sequence=new_seq,
                        log_prob=new_log_prob,
                        length=node.length + 1
                    )
                    all_candidates.append(candidate)

            if not all_candidates:
                break

            # Sort all candidates and keep the top beam_width
            all_candidates.sort(reverse=True)
            beams = all_candidates[:self.beam_width]

            # Early stopping if the worst finished beam is better than the best active beam
            if len(finished_beams) >= self.beam_width:
                finished_beams.sort(reverse=True)
                if finished_beams[0] > beams[0]:
                    break

        # Combine finished and active beams, return the best one
        final_beams = finished_beams + beams
        final_beams.sort(reverse=True)
        
        return final_beams[0].sequence
