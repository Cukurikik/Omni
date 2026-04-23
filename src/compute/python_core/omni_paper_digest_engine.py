# ===========================================================================
# OMNI PAPER DIGEST ENGINE (SEMESTER 5 — BATCH 12)
# ===========================================================================
# Absorbed From  : mli/paper-reading
# Logic Inherited: Compute Layer (ML Research Paper Analysis & Knowledge Extraction)
# ===========================================================================
#
# DEEP LEARNING ABSORBED:
#   Mu Li's paper-reading curates and dissects foundational ML papers:
#   Attention Is All You Need, ResNet, BERT, GPT, ViT, Diffusion Models, etc.
#   The pattern: for each paper, extract (1) core innovation, (2) architecture
#   diagram, (3) key equations, (4) ablation results, (5) limitations.
#   OMNI absorbs this taxonomy to build a structured paper analyzer.
#
"""
OMNI Paper Digest Engine
========================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
import logging
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err

logger = logging.getLogger("OmniPaperDigestEngine")


@dataclass
class PaperSection:
    """A structured section of a research paper."""
    heading: str
    content: str
    word_count: int = 0

    def __post_init__(self):
        self.word_count = len(self.content.split())


@dataclass
class PaperDigest:
    """Complete structured analysis of an ML research paper."""
    title: str
    authors: List[str]
    year: int
    domain: str
    sections: List[PaperSection] = field(default_factory=list)
    core_innovation: str = ""
    key_equations: List[str] = field(default_factory=list)
    architecture_components: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    citations_count: int = 0
    relevance_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        return {
            "title": self.title, "authors": self.authors, "year": self.year,
            "domain": self.domain, "core_innovation": self.core_innovation,
            "key_equations": self.key_equations,
            "architecture_components": self.architecture_components,
            "limitations": self.limitations,
            "section_count": len(self.sections),
            "total_words": sum(s.word_count for s in self.sections),
            "citations": self.citations_count,
            "relevance_score": round(self.relevance_score, 3)
        }


# Canonical ML paper taxonomy (from mli/paper-reading)
PAPER_TAXONOMY: Dict[str, List[str]] = {
    "transformer": ["attention", "self-attention", "multi-head", "positional encoding", "encoder-decoder"],
    "cnn": ["convolution", "pooling", "resnet", "vgg", "inception", "skip connection"],
    "diffusion": ["denoising", "noise schedule", "unet", "latent space", "ddpm", "ddim"],
    "nlp": ["tokenization", "embedding", "bert", "gpt", "language model", "fine-tuning"],
    "vision": ["object detection", "segmentation", "yolo", "ssd", "feature pyramid"],
    "reinforcement": ["reward", "policy gradient", "q-learning", "ppo", "actor-critic"],
    "generative": ["gan", "vae", "autoregressive", "flow", "normalizing flow"],
}


class OmniPaperDigestEngine:
    """
    Structured ML research paper analyzer inspired by mli/paper-reading.

    Capabilities:
        - Parse papers into structured sections
        - Classify papers by ML domain taxonomy
        - Extract core innovation, equations, architecture, limitations
        - Score relevance to OMNI ecosystem themes
    """

    def __init__(self):
        """Initialize OmniPaperDigestEngine."""
        self._paper_library: Dict[str, PaperDigest] = {}
        logger.info("[OmniPaperDigest] Research analysis engine online.")

    def _classify_domain(self, text: str) -> str:
        """Classifies paper domain by keyword frequency in taxonomy."""
        text_lower = text.lower()
        scores: Dict[str, int] = {}
        for domain, keywords in PAPER_TAXONOMY.items():
            scores[domain] = sum(1 for kw in keywords if kw in text_lower)
        if not scores or max(scores.values()) == 0:
            return "general"
        return max(scores, key=scores.get)

    def _extract_equations(self, text: str) -> List[str]:
        """Extracts mathematical notation patterns from paper text."""
        # Match common LaTeX-style or inline math patterns
        patterns = [
            r"(?:loss|L)\s*=\s*[^.]+",           # Loss functions
            r"(?:softmax|sigmoid|relu)\([^)]+\)",  # Activation functions
            r"Attention\([^)]+\)",                  # Attention formula
            r"[a-zA-Z]+\s*=\s*\w+\s*[*/+-]\s*\w+", # Simple equations
        ]
        equations = []
        for pat in patterns:
            matches = re.findall(pat, text, re.IGNORECASE)
            equations.extend(m.strip() for m in matches[:3])
        return equations[:5]

    def analyze_paper(
        self, title: str, authors: List[str], year: int,
        abstract: str, body_text: str = ""
    ) -> Dict[str, Any]:
        """
        Performs full structured analysis of a research paper.

        Args:
            title: Paper title.
            authors: List of author names.
            year: Publication year.
            abstract: Paper abstract text.
            body_text: Optional full paper body text.

        Returns:
            Structured PaperDigest with domain classification and extracted insights.
        """
        if not title or not abstract:
            return {"status": "error", "error": "Title and abstract are required."}

        full_text = f"{title} {abstract} {body_text}"
        domain = self._classify_domain(full_text)

        # Build sections
        sections = [PaperSection(heading="Abstract", content=abstract)]
        if body_text:
            # Split body into paragraphs as pseudo-sections
            paragraphs = [p.strip() for p in body_text.split("\n\n") if p.strip()]
            for i, para in enumerate(paragraphs[:10]):
                sections.append(PaperSection(heading=f"Section {i+1}", content=para))

        # Extract structured insights
        equations = self._extract_equations(full_text)
        arch_keywords = [kw for kw in PAPER_TAXONOMY.get(domain, []) if kw.lower() in full_text.lower()]

        # Relevance scoring: how relevant is this paper to OMNI compute engines
        relevance_keywords = ["production", "efficient", "real-time", "scalable", "deployment", "inference"]
        relevance = sum(1 for rk in relevance_keywords if rk in full_text.lower()) / len(relevance_keywords)

        digest = PaperDigest(
            title=title, authors=authors, year=year, domain=domain,
            sections=sections, core_innovation=abstract[:200],
            key_equations=equations, architecture_components=arch_keywords,
            limitations=["Computational cost not analyzed"] if "cost" not in full_text.lower() else [],
            citations_count=0, relevance_score=relevance
        )

        self._paper_library[title] = digest
        return {"status": "success", "data": digest.to_dict()}

    def search_library(self, query: str) -> Dict[str, Any]:
        """Searches the analyzed paper library by keyword."""
        q = query.lower()
        results = [
            d.to_dict() for d in self._paper_library.values()
            if q in d.title.lower() or q in d.domain
        ]
        return {"status": "success", "data": {"query": query, "results": results, "count": len(results)}}

    def get_library_stats(self) -> Dict[str, Any]:
        """Performs get library stats operation for OmniPaperDigestEngine."""
        domains: Dict[str, int] = {}
        for d in self._paper_library.values():
            domains[d.domain] = domains.get(d.domain, 0) + 1
        return {"status": "success", "data": {
            "total_papers": len(self._paper_library), "domain_distribution": domains
        }}

    def evaluate_health(self) -> Dict[str, Any]:
        """Performs evaluate health operation for OmniPaperDigestEngine."""
        return {
            "engine": "OmniPaperDigestEngine", "layer": "Compute", "status": "healthy",
            "papers_analyzed": len(self._paper_library),
            "taxonomy_domains": len(PAPER_TAXONOMY),
            "learned_from": "mli/paper-reading"
        }

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-paper-digest",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }
