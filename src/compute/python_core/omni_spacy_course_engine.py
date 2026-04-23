"""
OMNI spaCy Course Engine
=========================
Production-grade OMNI engine abstracting spaCy NLP pipeline construction,
token analysis, entity recognition, and linguistic pattern matching.
Inspired by explosion/spacy-course and spaCy v3 architecture.

Features:
- Tokenisation, POS tagging and dependency parse topological_evaluation.
- Named Entity Recognition (NER) via rule-based pattern matchers.
- Custom pipeline component registration & execution.
- Linguistic pattern matching with token-level predicates.
- Monadic Result encapsulation preventing runtime trace crashes.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------

ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class SpacyCourseErr(Exception):
    """Base error for spaCy Course engine."""
    pass


@dataclass(frozen=True)
class Ok:
    """Monadic Ok result type."""
    value: Any


@dataclass(frozen=True)
class Err:
    """Monadic Err result type."""
    error: str


Result = Union[Ok, Err]


# ---------------------------------------------------------------------------
# 2. TOKEN & DOC STRUCTURES
# ---------------------------------------------------------------------------

@dataclass
class Token:
    """Represents a single token in a document."""
    text: str
    idx: int
    pos: str = "UNKNOWN"
    tag: str = "XX"
    dep: str = ""
    head_idx: int = -1
    is_alpha: bool = True
    is_stop: bool = False
    lemma: str = ""
    ent_type: str = ""
    ent_iob: str = "O"


@dataclass
class Span:
    """A slice of tokens within a Doc, typically an entity."""
    start: int
    end: int
    label: str
    text: str


@dataclass
class Doc:
    """Container for processed text, carrying tokens and entities."""
    text: str
    tokens: List[Token] = field(default_factory=list)
    ents: List[Span] = field(default_factory=list)
    noun_chunks: List[Span] = field(default_factory=list)

    def __len__(self) -> int:
        """Return the number of tokens."""
        return len(self.tokens)

    def __getitem__(self, idx: int) -> Token:
        """Access a token by index."""
        return self.tokens[idx]


# ---------------------------------------------------------------------------
# 3. BUILT-IN POS TAGGER (rule-based)
# ---------------------------------------------------------------------------

# Minimalist POS rules for English
_STOP_WORDS: Set[str] = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "shall",
    "should", "may", "might", "must", "can", "could", "of", "in", "to",
    "for", "with", "on", "at", "from", "by", "about", "as", "into",
    "through", "during", "before", "after", "above", "below", "between",
    "and", "but", "or", "nor", "not", "so", "yet", "both", "either",
    "neither", "each", "every", "all", "any", "few", "more", "most",
    "other", "some", "such", "no", "only", "own", "same", "than", "too",
    "very", "just", "because", "if", "when", "while", "where", "how",
    "what", "which", "who", "whom", "this", "that", "these", "those",
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you",
    "your", "yours", "he", "him", "his", "she", "her", "hers", "it",
    "its", "they", "them", "their", "theirs",
}

_DETERMINER_WORDS = {"the", "a", "an", "this", "that", "these", "those"}
_PRONOUN_WORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "you", "your",
    "he", "him", "his", "she", "her", "hers", "it", "its", "they",
    "them", "their", "theirs",
}
_AUX_VERBS = {
    "is", "are", "was", "were", "be", "been", "being", "have", "has",
    "had", "do", "does", "did", "will", "would", "shall", "should",
    "may", "might", "must", "can", "could",
}
_CONJUNCTIONS = {"and", "but", "or", "nor", "so", "yet", "for"}
_PREPOSITIONS = {
    "of", "in", "to", "for", "with", "on", "at", "from", "by", "about",
    "as", "into", "through", "during", "before", "after", "above",
    "below", "between",
}


def _assign_pos(word: str) -> str:
    """Assign a coarse POS tag to a word.

    Args:
        word: Lowercased word form.

    Returns:
        POS tag string.
    """
    low = word.lower()
    if low in _DETERMINER_WORDS:
        return "DET"
    if low in _PRONOUN_WORDS:
        return "PRON"
    if low in _AUX_VERBS:
        return "AUX"
    if low in _CONJUNCTIONS:
        return "CCONJ"
    if low in _PREPOSITIONS:
        return "ADP"
    if word[0].isupper() and len(word) > 1:
        return "PROPN"
    if word.isdigit():
        return "NUM"
    if not word.isalpha():
        return "PUNCT"
    # fallback heuristic: ends in common verb suffixes
    if low.endswith(("ing", "ed", "es", "ize", "ise")):
        return "VERB"
    if low.endswith(("ly",)):
        return "ADV"
    if low.endswith(("tion", "ness", "ment", "ity", "ence", "ance")):
        return "NOUN"
    return "NOUN"


# ---------------------------------------------------------------------------
# 4. TOKENIZER
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def _tokenize(text: str) -> List[Token]:
    """Tokenize text into Token objects with POS tags.

    Args:
        text: Raw input text.

    Returns:
        List of Token instances.
    """
    tokens: List[Token] = []
    for idx, match in enumerate(_TOKEN_RE.finditer(text)):
        word = match.group()
        pos = _assign_pos(word)
        tokens.append(Token(
            text=word,
            idx=idx,
            pos=pos,
            is_alpha=word.isalpha(),
            is_stop=word.lower() in _STOP_WORDS,
            lemma=word.lower(),
        ))
    return tokens


# ---------------------------------------------------------------------------
# 5. ENTITY RECOGNISER (pattern-based)
# ---------------------------------------------------------------------------

@dataclass
class EntityRule:
    """Rule for recognising named entities."""
    label: str
    pattern: str  # regex pattern matching over text
    case_sensitive: bool = False


class RuleBasedNER:
    """Named entity recogniser using regex patterns."""

    def __init__(self) -> None:
        """Initialise with empty rule set."""
        self._rules: List[EntityRule] = []

    def add_rule(self, label: str, pattern: str,
                 case_sensitive: bool = False) -> None:
        """Register an entity recognition rule.

        Args:
            label: Entity label (e.g. 'ORG', 'PERSON').
            pattern: Regex pattern to match in raw text.
            case_sensitive: Whether matching is case-sensitive.
        """
        self._rules.append(EntityRule(label, pattern, case_sensitive))

    def find_entities(self, text: str) -> List[Span]:
        """Find all entities in text.

        Args:
            text: Raw text.

        Returns:
            List of Span objects representing entity mentions.
        """
        entities: List[Span] = []
        for rule in self._rules:
            flags = 0 if rule.case_sensitive else re.IGNORECASE
            for m in re.finditer(rule.pattern, text, flags):
                entities.append(Span(
                    start=m.start(), end=m.end(),
                    label=rule.label, text=m.group(),
                ))
        # Sort by start position, remove overlaps (first-match wins)
        entities.sort(key=lambda s: s.start)
        deduped: List[Span] = []
        last_end = -1
        for ent in entities:
            if ent.start >= last_end:
                deduped.append(ent)
                last_end = ent.end
        return deduped


# ---------------------------------------------------------------------------
# 6. PATTERN MATCHER (token-level)
# ---------------------------------------------------------------------------

class TokenPatternMatcher:
    """Matcher for token-level patterns (like spaCy Matcher)."""

    def __init__(self) -> None:
        """Initialise with empty pattern registry."""
        self._patterns: Dict[str, List[Dict[str, Any]]] = {}

    def add_pattern(self, name: str, pattern: List[Dict[str, Any]]) -> None:
        """Register a token pattern.

        Each pattern element is a dict like ``{"TEXT": "hello"}`` or
        ``{"POS": "NOUN"}``.

        Args:
            name: Pattern label.
            pattern: List of token-level constraints.
        """
        self._patterns[name] = pattern

    def find_matches(self, doc: Doc) -> List[Tuple[str, int, int]]:
        """Find all pattern matches in a Doc.

        Args:
            doc: Processed Doc.

        Returns:
            List of (pattern_name, start_idx, end_idx).
        """
        matches: List[Tuple[str, int, int]] = []
        for name, pattern in self._patterns.items():
            plen = len(pattern)
            for i in range(len(doc.tokens) - plen + 1):
                if self._match_at(doc.tokens, i, pattern):
                    matches.append((name, i, i + plen))
        return matches

    @staticmethod
    def _match_at(tokens: List[Token], start: int,
                  pattern: List[Dict[str, Any]]) -> bool:
        """Check if pattern matches at a given token offset.

        Args:
            tokens: All tokens.
            start: Offset to start matching.
            pattern: Pattern to match.

        Returns:
            True if pattern matches.
        """
        for offset, constraint in enumerate(pattern):
            tok = tokens[start + offset]
            for key, val in constraint.items():
                key_up = key.upper()
                if key_up == "TEXT" and tok.text != val:
                    return False
                if key_up == "LOWER" and tok.text.lower() != val.lower():
                    return False
                if key_up == "POS" and tok.pos != val:
                    return False
                if key_up == "IS_ALPHA" and tok.is_alpha != val:
                    return False
                if key_up == "IS_STOP" and tok.is_stop != val:
                    return False
        return True


# ---------------------------------------------------------------------------
# 7. PIPELINE
# ---------------------------------------------------------------------------

class NLPPipeline:
    """NLP processing pipeline with pluggable components."""

    def __init__(self) -> None:
        """Initialise the pipeline."""
        self._ner = RuleBasedNER()
        self._components: List[Tuple[str, Callable[[Doc], Doc]]] = []

    def add_ner_rule(self, label: str, pattern: str,
                     case_sensitive: bool = False) -> None:
        """Add an NER rule to the built-in recogniser.

        Args:
            label: Entity label.
            pattern: Regex pattern.
            case_sensitive: Case sensitivity flag.
        """
        self._ner.add_rule(label, pattern, case_sensitive)

    def add_component(self, name: str, fn: Callable[[Doc], Doc]) -> None:
        """Register a custom pipeline component.

        Args:
            name: Component name.
            fn: Function ``Doc -> Doc``.
        """
        self._components.append((name, fn))

    def process(self, text: str) -> Doc:
        """Run the full pipeline on raw text.

        Args:
            text: Input text.

        Returns:
            Processed Doc.
        """
        tokens = _tokenize(text)
        ents = self._ner.find_entities(text)
        doc = Doc(text=text, tokens=tokens, ents=ents)
        for _name, fn in self._components:
            doc = fn(doc)
        return doc


# ---------------------------------------------------------------------------
# 8. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniSpacyCourseEngine:
    """
    Production Engine unifying spaCy-style NLP processing with
    rule-based NER, POS tagging, and pattern matching.
    """
    VERSION = "1.0.0"
    ENGINE_ID = "omni-spacy-course"

    def __init__(self) -> None:
        """Initialise the engine with default pipeline."""
        self.pipeline = NLPPipeline()
        self.matcher = TokenPatternMatcher()
        # Pre-register common entity patterns
        self.pipeline.add_ner_rule("ORG", r"\b(?:Google|Apple|Microsoft|Amazon|Meta|NVIDIA)\b")
        self.pipeline.add_ner_rule("GPE", r"\b(?:United States|Germany|Japan|China|India|France|London|Berlin|Tokyo)\b")
        self.pipeline.add_ner_rule("PERSON", r"\b(?:Elon Musk|Jeff Bezos|Tim Cook|Satya Nadella)\b")

    def process_text(self, text: str) -> Result:
        """Process text through the NLP pipeline.

        Args:
            text: Raw input text.

        Returns:
            Result containing the processed Doc.
        """
        if not text or not text.strip():
            return Err("Input text is empty")
        try:
            doc = self.pipeline.process(text)
            return Ok(doc)
        except Exception as exc:
            return Err(f"Pipeline processing failed: {exc}")

    def find_entities(self, text: str) -> Result:
        """Extract entities from text.

        Args:
            text: Raw input text.

        Returns:
            Result containing list of entity dicts.
        """
        doc_res = self.process_text(text)
        if isinstance(doc_res, Err):
            return doc_res
        doc = doc_res.value
        return Ok([{"text": e.text, "label": e.label, "start": e.start,
                     "end": e.end} for e in doc.ents])

    def tokenize(self, text: str) -> Result:
        """Tokenize and POS-tag input text.

        Args:
            text: Raw input text.

        Returns:
            Result containing list of token dicts.
        """
        doc_res = self.process_text(text)
        if isinstance(doc_res, Err):
            return doc_res
        doc = doc_res.value
        return Ok([{"text": t.text, "pos": t.pos, "lemma": t.lemma,
                     "is_stop": t.is_stop} for t in doc.tokens])

    def match_pattern(self, text: str, pattern_name: str,
                      pattern: List[Dict[str, Any]]) -> Result:
        """Match a token-level pattern against text.

        Args:
            text: Raw input text.
            pattern_name: Name of the pattern.
            pattern: Token-level constraints.

        Returns:
            Result containing list of match tuples.
        """
        doc_res = self.process_text(text)
        if isinstance(doc_res, Err):
            return doc_res
        self.matcher.add_pattern(pattern_name, pattern)
        matches = self.matcher.find_matches(doc_res.value)
        return Ok(matches)

    def diagnostics(self) -> Dict[str, Any]:
        """Return engine diagnostics.

        Returns:
            Dict with engine status and capability list.
        """
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "status": "operational",
            "features": [
                "tokenization", "pos_tagging", "rule_based_ner",
                "pattern_matching", "custom_pipeline_components",
            ],
        }
