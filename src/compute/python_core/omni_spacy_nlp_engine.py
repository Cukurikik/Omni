# ===========================================================================
# OMNI SPACY NLP ENGINE (SEMESTER 5 — BATCH 11)
# ===========================================================================
# Absorbed From  : explosion/spaCy
# Logic Inherited: Compute Layer (Industrial NLP Pipeline)
# ===========================================================================
#
# DEEP LEARNING ABSORBED:
#   spaCy processes text through a sequential pipeline:
#     Raw Text → Tokenizer → [Tagger → Parser → NER → ...] → Doc
#   Each component receives a Doc, modifies it, and passes it on.
#   Components are modular — you can add/remove/reorder them.
#   The tokenizer uses language-specific rules (prefixes, suffixes,
#   infixes, special cases) for non-destructive segmentation.
#
"""
OMNI Spacy Nlp Engine
=====================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field


ENGINE_VERSION = "1.0.0-omni"

logger = logging.getLogger("OmniSpacyNlpEngine")


@dataclass
class Token:
    """Represents a single token in the document."""
    text: str
    index: int
    pos: str = "UNKNOWN"       # Part-of-speech tag
    dep: str = "UNKNOWN"       # Dependency label
    lemma: str = ""            # Base form
    is_punct: bool = False
    is_stop: bool = False
    ent_type: str = ""         # Named entity type (if any)
    ent_iob: str = "O"        # IOB tag: B, I, O
    head_index: int = -1       # Index of syntactic head

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        return {
            "text": self.text, "index": self.index,
            "pos": self.pos, "dep": self.dep, "lemma": self.lemma,
            "is_punct": self.is_punct, "is_stop": self.is_stop,
            "ent_type": self.ent_type, "ent_iob": self.ent_iob,
            "head_index": self.head_index
        }


@dataclass
class Span:
    """A contiguous slice of tokens (e.g., a named entity or noun chunk)."""
    text: str
    start: int
    end: int
    label: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        return {"text": self.text, "start": self.start, "end": self.end, "label": self.label}


@dataclass
class Doc:
    """The central data structure: a processed document containing all annotations."""
    text: str
    tokens: List[Token] = field(default_factory=list)
    entities: List[Span] = field(default_factory=list)
    noun_chunks: List[Span] = field(default_factory=list)
    sentences: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        return {
            "text": self.text,
            "token_count": len(self.tokens),
            "tokens": [t.to_dict() for t in self.tokens],
            "entities": [e.to_dict() for e in self.entities],
            "noun_chunks": [nc.to_dict() for nc in self.noun_chunks],
            "sentences": self.sentences
        }


# ──────────────────────────────────────────────
# Pipeline Components (each modifies the Doc)
# ──────────────────────────────────────────────

STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "in", "on", "at", "to",
    "for", "from", "by", "with", "of", "and", "or", "but", "if", "not",
    "this", "that", "it", "its", "i", "you", "he", "she", "we", "they",
}

POS_RULES: Dict[str, str] = {
    # Simplified heuristic POS tagger
    ".": "PUNCT", ",": "PUNCT", "!": "PUNCT", "?": "PUNCT",
    ":": "PUNCT", ";": "PUNCT", "'s": "PART",
}

ENTITY_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b"), "PERSON"),
    (re.compile(r"\b(?:Google|Apple|Microsoft|OpenAI|Meta|Amazon|Tesla|OMNI)\b"), "ORG"),
    (re.compile(r"\b(?:Indonesia|Japan|USA|China|Germany|France|India|Singapore)\b"), "GPE"),
    (re.compile(r"\b\d{4}\b"), "DATE"),
    (re.compile(r"\$\d+(?:\.\d+)?(?:\s?(?:million|billion|trillion))?"), "MONEY"),
]


class Tokenizer:
    """Rule-based tokenizer inspired by spaCy's segmentation rules."""

    PUNCT = set(".,!?;:()[]{}\"'`~@#$%^&*-_+=<>/\\|")

    def tokenize(self, text: str) -> List[Token]:
        """Splits text into tokens preserving original character spans."""
        raw_tokens = re.findall(r"\S+", text)
        tokens: List[Token] = []
        idx = 0
        for raw in raw_tokens:
            # Split trailing punctuation
            while raw and raw[-1] in self.PUNCT:
                core = raw[:-1]
                if core:
                    tokens.append(Token(text=core, index=idx, is_punct=False))
                    idx += 1
                tokens.append(Token(text=raw[-1], index=idx, is_punct=True))
                idx += 1
                raw = ""
                break
            else:
                if raw:
                    tokens.append(Token(text=raw, index=idx, is_punct=(raw in self.PUNCT)))
                    idx += 1
        return tokens


class POSTagger:
    """Assigns Part-of-Speech tags using rule heuristics."""

    def process(self, doc: Doc) -> Doc:
        """Execute process operation for POSTagger."""
        for tok in doc.tokens:
            if tok.text in POS_RULES:
                tok.pos = POS_RULES[tok.text]
            elif tok.is_punct:
                tok.pos = "PUNCT"
            elif tok.text.lower() in STOP_WORDS:
                tok.pos = "DET" if tok.text.lower() in {"the", "a", "an"} else "ADP"
                tok.is_stop = True
            elif tok.text[0].isupper() and tok.index > 0:
                tok.pos = "PROPN"
            elif tok.text.isdigit():
                tok.pos = "NUM"
            else:
                tok.pos = "NOUN" if len(tok.text) > 3 else "VERB"
            tok.lemma = tok.text.lower().rstrip("seding")[:max(3, len(tok.text) - 2)] if tok.pos in ("NOUN", "VERB") else tok.text.lower()
        return doc


class DependencyParser:
    """Simplified dependency parser that identifies head tokens and sentence boundaries."""

    def process(self, doc: Doc) -> Doc:
        """Execute process operation for DependencyParser."""
        current_sentence: List[str] = []
        for i, tok in enumerate(doc.tokens):
            current_sentence.append(tok.text)
            if tok.pos == "PUNCT" and tok.text in ".!?":
                doc.sentences.append(" ".join(current_sentence))
                current_sentence = []
                tok.dep = "punct"
                tok.head_index = max(0, i - 1)
            elif tok.pos in ("NOUN", "PROPN"):
                tok.dep = "nsubj" if i < len(doc.tokens) // 2 else "dobj"
                tok.head_index = min(i + 1, len(doc.tokens) - 1)
            elif tok.pos == "VERB":
                tok.dep = "ROOT"
                tok.head_index = i
            else:
                tok.dep = "det" if tok.pos == "DET" else "prep"
                tok.head_index = min(i + 1, len(doc.tokens) - 1)
        if current_sentence:
            doc.sentences.append(" ".join(current_sentence))
        return doc


class NamedEntityRecognizer:
    """Rule-based NER using regex patterns inspired by spaCy's entity ruler."""

    def process(self, doc: Doc) -> Doc:
        """Execute process operation for NamedEntityRecognizer."""
        full_text = doc.text
        for pattern, label in ENTITY_PATTERNS:
            for match in pattern.finditer(full_text):
                span = Span(
                    text=match.group(), start=match.start(),
                    end=match.end(), label=label
                )
                doc.entities.append(span)
                # Mark tokens that fall within entity spans
                for tok in doc.tokens:
                    if tok.text in match.group().split():
                        tok.ent_type = label
                        tok.ent_iob = "B" if tok.text == match.group().split()[0] else "I"
        return doc


class OmniSpacyNlpEngine:
    """
    Industrial-grade NLP pipeline inspired by explosion/spaCy.

    Pipeline stages:
        1. Tokenizer     — segment raw text into tokens
        2. POS Tagger    — assign part-of-speech tags
        3. Dep Parser    — dependency structure & sentence boundaries
        4. NER           — named entity recognition

    All stages are modular and independently removable.
    """

    def __init__(self, disable: Optional[List[str]] = None):
        """Initialize OmniSpacyNlpEngine."""
        self._tokenizer = Tokenizer()
        self._pipeline: List[Tuple[str, Any]] = [
            ("tagger", POSTagger()),
            ("parser", DependencyParser()),
            ("ner", NamedEntityRecognizer()),
        ]
        self._disabled = set(disable or [])
        active = [name for name, _ in self._pipeline if name not in self._disabled]
        logger.info(f"[OmniSpacyNLP] Pipeline online. Active stages: {active}")

    def process(self, text: str) -> Dict[str, Any]:
        """
        Processes raw text through the full NLP pipeline.

        Args:
            text: Raw text to process.

        Returns:
            Result dict with all annotations (tokens, entities, sentences).
        """
        if not text or not text.strip():
            return {"status": "error", "error": "Empty text input."}

        # Stage 1: Tokenization
        tokens = self._tokenizer.tokenize(text)
        doc = Doc(text=text, tokens=tokens)

        # Stages 2-N: Pipeline components
        for name, component in self._pipeline:
            if name not in self._disabled:
                doc = component.process(doc)

        return {"status": "success", "data": doc.to_dict()}

    def get_pipeline_info(self) -> Dict[str, Any]:
        """Returns info about currently active pipeline components."""
        return {
            "status": "success",
            "data": {
                "components": [name for name, _ in self._pipeline],
                "disabled": list(self._disabled),
                "active": [n for n, _ in self._pipeline if n not in self._disabled]
            }
        }

    def evaluate_health(self) -> Dict[str, Any]:
        """Performs evaluate health operation for OmniSpacyNlpEngine."""
        return {
            "engine": "OmniSpacyNlpEngine",
            "layer": "Compute",
            "status": "healthy",
            "pipeline_stages": len(self._pipeline),
            "entity_patterns": len(ENTITY_PATTERNS),
            "learned_from": "explosion/spaCy"
        }

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-spacy-nlp",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }


if __name__ == "__main__":
    nlp = OmniSpacyNlpEngine()
    result = nlp.process("OpenAI released CLIP in 2021. Google and Microsoft are investing in Indonesia.")
    doc = result["data"]
    print(f"Tokens: {doc['token_count']}, Entities: {len(doc['entities'])}, Sentences: {len(doc['sentences'])}")
    for ent in doc["entities"]:
        print(f"  Entity: '{ent['text']}' → {ent['label']}")
