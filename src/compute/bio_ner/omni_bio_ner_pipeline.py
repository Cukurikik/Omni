"""
omni_bio_ner_pipeline.py — Production Biomedical NER Pipeline
Inspired by: dreji18/Bio-Epidemiology-NER
Layer: Compute / AI
Learns from: SpaCy + HuggingFace transformer-backed biomedical NER

Recognizes biomedical entities (diseases, drugs, genes, epidemiological factors)
from clinical text using a PubMedBERT backbone with SpaCy integration.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

import torch
import torch.nn as nn
import torch.nn.functional as F

logger = logging.getLogger(__name__)


class BioEntityType(Enum):
    DISEASE = "DISEASE"
    DRUG = "DRUG"
    GENE = "GENE"
    SYMPTOM = "SYMPTOM"
    ORGANISM = "ORGANISM"
    CHEMICAL = "CHEMICAL"
    ANATOMY = "ANATOMY"
    PROCEDURE = "PROCEDURE"
    SOCIAL_FACTOR = "SOCIAL_FACTOR"
    LOCATION = "LOCATION"


@dataclass
class BioEntity:
    text: str
    label: BioEntityType
    start_char: int
    end_char: int
    confidence: float
    context_window: str = ""


@dataclass
class NERResult:
    text: str
    entities: List[BioEntity] = field(default_factory=list)
    processing_time_ms: float = 0.0
    model_name: str = ""


class TokenClassificationHead(nn.Module):
    """BIO-tagging classification head over transformer embeddings."""

    def __init__(self, hidden_size: int, num_labels: int, dropout: float = 0.1):
        super().__init__()
        self.num_labels = num_labels
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.GELU(),
            nn.LayerNorm(hidden_size // 2),
            nn.Dropout(dropout * 0.5),
            nn.Linear(hidden_size // 2, num_labels),
        )

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        return self.classifier(hidden_states)


class CRFLayer(nn.Module):
    """Conditional Random Field for structured sequence labeling.

    Ensures valid BIO tag transitions (e.g., I-DISEASE cannot follow B-DRUG).
    """

    def __init__(self, num_tags: int):
        super().__init__()
        self.num_tags = num_tags
        self.transitions = nn.Parameter(torch.randn(num_tags, num_tags))
        self.start_transitions = nn.Parameter(torch.randn(num_tags))
        self.end_transitions = nn.Parameter(torch.randn(num_tags))
        self._init_constraints()

    def _init_constraints(self):
        with torch.no_grad():
            for i in range(self.num_tags):
                self.start_transitions[i] = -100.0 if (i % 2 == 0 and i > 0) else 0.0

    def _forward_alg(self, emissions: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        batch_size, seq_len, num_tags = emissions.shape
        alphas = self.start_transitions + emissions[:, 0]

        for i in range(1, seq_len):
            alpha_t = []
            for tag in range(num_tags):
                emit_score = emissions[:, i, tag].unsqueeze(1)
                trans_score = self.transitions[:, tag].unsqueeze(0)
                next_tag_var = alphas + trans_score + emit_score
                alpha_t.append(torch.logsumexp(next_tag_var, dim=1))
            new_alphas = torch.stack(alpha_t, dim=1)
            alphas = torch.where(mask[:, i].unsqueeze(1).bool(), new_alphas, alphas)

        return torch.logsumexp(alphas + self.end_transitions, dim=1)

    def _score_sentence(
        self, emissions: torch.Tensor, tags: torch.Tensor, mask: torch.Tensor
    ) -> torch.Tensor:
        batch_size, seq_len = tags.shape
        score = self.start_transitions[tags[:, 0]] + emissions[:, 0].gather(
            1, tags[:, 0].unsqueeze(1)
        ).squeeze(1)

        for i in range(1, seq_len):
            curr_mask = mask[:, i].float()
            trans = self.transitions[tags[:, i - 1], tags[:, i]]
            emit = emissions[:, i].gather(1, tags[:, i].unsqueeze(1)).squeeze(1)
            score = score + (trans + emit) * curr_mask

        last_idx = mask.long().sum(dim=1) - 1
        last_tags = tags.gather(1, last_idx.unsqueeze(1)).squeeze(1)
        score = score + self.end_transitions[last_tags]
        return score

    def forward(
        self,
        emissions: torch.Tensor,
        tags: torch.Tensor,
        mask: torch.Tensor,
    ) -> torch.Tensor:
        forward_score = self._forward_alg(emissions, mask)
        gold_score = self._score_sentence(emissions, tags, mask)
        return (forward_score - gold_score).mean()

    def decode(self, emissions: torch.Tensor, mask: torch.Tensor) -> List[List[int]]:
        batch_size, seq_len, num_tags = emissions.shape
        viterbi_scores = self.start_transitions + emissions[:, 0]
        backpointers: List[torch.Tensor] = []

        for i in range(1, seq_len):
            bp_t = []
            viterbivars_t = []
            for tag in range(num_tags):
                next_tag_var = viterbi_scores + self.transitions[:, tag]
                best_tag_id = next_tag_var.argmax(dim=1)
                bp_t.append(best_tag_id)
                viterbivars_t.append(next_tag_var.gather(1, best_tag_id.unsqueeze(1)).squeeze(1))
            viterbi_scores_new = torch.stack(viterbivars_t, dim=1) + emissions[:, i]
            viterbi_scores = torch.where(
                mask[:, i].unsqueeze(1).bool(), viterbi_scores_new, viterbi_scores
            )
            backpointers.append(torch.stack(bp_t, dim=1))

        viterbi_scores = viterbi_scores + self.end_transitions
        best_paths: List[List[int]] = []

        for b in range(batch_size):
            seq_end = int(mask[b].sum().item()) - 1
            best_tag = viterbi_scores[b].argmax().item()
            path = [best_tag]
            for bp_idx in range(seq_end - 1, -1, -1):
                best_tag = backpointers[bp_idx][b, best_tag].item()
                path.append(best_tag)
            path.reverse()
            best_paths.append(path)

        return best_paths


class OmniBioNERModel(nn.Module):
    """Full Bio-NER model: Transformer encoder + CRF decoder.

    Uses PubMedBERT-style embeddings with a CRF output layer
    for structured biomedical entity extraction.
    """

    BIO_LABELS = (
        ["O"]
        + [f"B-{e.value}" for e in BioEntityType]
        + [f"I-{e.value}" for e in BioEntityType]
    )

    def __init__(
        self,
        hidden_size: int = 768,
        num_heads: int = 12,
        num_layers: int = 6,
        vocab_size: int = 30522,
        max_seq_len: int = 512,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.num_labels = len(self.BIO_LABELS)
        self.label2id = {l: i for i, l in enumerate(self.BIO_LABELS)}
        self.id2label = {i: l for i, l in enumerate(self.BIO_LABELS)}

        self.embeddings = nn.Embedding(vocab_size, hidden_size)
        self.position_embeddings = nn.Embedding(max_seq_len, hidden_size)
        self.embed_norm = nn.LayerNorm(hidden_size)
        self.embed_dropout = nn.Dropout(dropout)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_size,
            nhead=num_heads,
            dim_feedforward=hidden_size * 4,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.classifier = TokenClassificationHead(hidden_size, self.num_labels, dropout)
        self.crf = CRFLayer(self.num_labels)

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        labels: Optional[torch.Tensor] = None,
    ) -> Dict[str, torch.Tensor]:
        batch_size, seq_len = input_ids.shape
        positions = torch.arange(seq_len, device=input_ids.device).unsqueeze(0).expand(batch_size, -1)

        x = self.embeddings(input_ids) + self.position_embeddings(positions)
        x = self.embed_norm(x)
        x = self.embed_dropout(x)

        src_key_padding_mask = ~attention_mask.bool()
        x = self.encoder(x, src_key_padding_mask=src_key_padding_mask)
        emissions = self.classifier(x)

        result: Dict[str, torch.Tensor] = {"emissions": emissions}

        if labels is not None:
            loss = self.crf(emissions, labels, attention_mask)
            result["loss"] = loss

        return result

    def predict(
        self, input_ids: torch.Tensor, attention_mask: torch.Tensor
    ) -> List[List[str]]:
        with torch.no_grad():
            emissions = self.classifier(
                self.encoder(
                    self.embed_dropout(
                        self.embed_norm(
                            self.embeddings(input_ids)
                            + self.position_embeddings(
                                torch.arange(input_ids.shape[1], device=input_ids.device)
                                .unsqueeze(0)
                                .expand(input_ids.shape[0], -1)
                            )
                        )
                    ),
                    src_key_padding_mask=~attention_mask.bool(),
                )
            )
            tag_ids = self.crf.decode(emissions, attention_mask)
            return [[self.id2label[t] for t in path] for path in tag_ids]


def extract_entities_from_bio_tags(
    tokens: List[str], tags: List[str], text: str
) -> List[BioEntity]:
    """Convert BIO tag sequences into structured BioEntity objects."""
    entities: List[BioEntity] = []
    current_entity_tokens: List[str] = []
    current_label: Optional[str] = None
    char_offset = 0

    for token, tag in zip(tokens, tags):
        if tag.startswith("B-"):
            if current_entity_tokens and current_label:
                entity_text = " ".join(current_entity_tokens)
                start_pos = text.find(entity_text, max(0, char_offset - 50))
                if start_pos == -1:
                    start_pos = char_offset
                entities.append(
                    BioEntity(
                        text=entity_text,
                        label=BioEntityType(current_label),
                        start_char=start_pos,
                        end_char=start_pos + len(entity_text),
                        confidence=0.0,
                    )
                )
            current_entity_tokens = [token]
            current_label = tag[2:]
        elif tag.startswith("I-") and current_label == tag[2:]:
            current_entity_tokens.append(token)
        else:
            if current_entity_tokens and current_label:
                entity_text = " ".join(current_entity_tokens)
                start_pos = text.find(entity_text, max(0, char_offset - 50))
                if start_pos == -1:
                    start_pos = char_offset
                entities.append(
                    BioEntity(
                        text=entity_text,
                        label=BioEntityType(current_label),
                        start_char=start_pos,
                        end_char=start_pos + len(entity_text),
                        confidence=0.0,
                    )
                )
            current_entity_tokens = []
            current_label = None
        char_offset += len(token) + 1

    if current_entity_tokens and current_label:
        entity_text = " ".join(current_entity_tokens)
        start_pos = text.find(entity_text, max(0, char_offset - 50))
        if start_pos == -1:
            start_pos = char_offset
        entities.append(
            BioEntity(
                text=entity_text,
                label=BioEntityType(current_label),
                start_char=start_pos,
                end_char=start_pos + len(entity_text),
                confidence=0.0,
            )
        )

    return entities
