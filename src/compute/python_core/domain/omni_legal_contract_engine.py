ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI LEGAL CONTRACT ENGINE — AI-Powered Contract & Legal Document Analysis
# ===========================================================================
# Source Paradigm: https://github.com/AlexAnys/awesome-openclaw-usecases-zh
# Domain Layer  : Domain (Legal / Contract Intelligence)
# Zero-Prod     : 100% Native — json, os, re, hashlib, real text processing
# ===========================================================================
"""
awesome-openclaw-usecases teaches us:
  1. Legal document structure parsing (clauses, sections, articles)
  2. Contract metadata extraction (parties, dates, obligations)
  3. Risk clause identification (indemnification, liability, termination)
  4. Contract comparison and diff analysis
  5. Obligation tracking and compliance monitoring
  6. Multi-jurisdiction legal template management

This engine distills those paradigms into OMNI-native Python for
automated contract analysis using regex NLP and structured extraction.
"""

import hashlib
import json
import os
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


# ── Data Models ──────────────────────────────────────────────────────────────

class ClauseRisk(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ContractType(Enum):
    NDA = "nda"
    SLA = "sla"
    MSA = "msa"
    EMPLOYMENT = "employment"
    LICENSE = "license"
    PARTNERSHIP = "partnership"
    SAAS = "saas"
    CUSTOM = "custom"


@dataclass
class ContractParty:
    name: str
    role: str           # "party_a" | "party_b" | "vendor" | "client"
    address: str = ""
    jurisdiction: str = ""


@dataclass
class ContractClause:
    section: str
    title: str
    content: str
    risk_level: ClauseRisk = ClauseRisk.LOW
    risk_reason: str = ""
    obligations: List[str] = field(default_factory=list)


@dataclass
class ContractMetadata:
    title: str = ""
    contract_type: str = ""
    effective_date: str = ""
    expiration_date: str = ""
    governing_law: str = ""
    parties: List[ContractParty] = field(default_factory=list)
    total_clauses: int = 0
    word_count: int = 0
    content_hash: str = ""


@dataclass
class ContractAnalysis:
    metadata: ContractMetadata = field(default_factory=ContractMetadata)
    clauses: List[ContractClause] = field(default_factory=list)
    risk_summary: Dict[str, int] = field(default_factory=dict)
    obligations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# ── Text Extractors ─────────────────────────────────────────────────────────

class ContractParser:
    """Parse and extract structured data from contract text."""

    # Date patterns
    DATE_PATTERNS = [
        r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
        r'\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b',
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
    ]

    # Party extraction patterns
    PARTY_PATTERNS = [
        r'(?:between|by and between)\s+([A-Z][A-Za-z\s,\.]+?)(?:\s*\()',
        r'"([A-Z][A-Za-z\s]+?)"\s*(?:hereinafter|hereafter)',
        r'(?:Party\s+[AB]|Licensor|Licensee|Vendor|Client|Employer|Employee):\s*(.+?)(?:\n|$)',
    ]

    @staticmethod
    def extract_dates(text: str) -> List[str]:
        dates = []
        for pattern in ContractParser.DATE_PATTERNS:
            dates.extend(re.findall(pattern, text, re.IGNORECASE))
        return list(set(dates))[:10]

    @staticmethod
    def extract_parties(text: str) -> List[ContractParty]:
        parties = []
        for pattern in ContractParser.PARTY_PATTERNS:
            matches = re.findall(pattern, text[:3000])
            for m in matches:
                name = m.strip().rstrip(",.")
                if len(name) > 3 and len(name) < 100:
                    parties.append(ContractParty(name=name, role="party"))
        return parties[:6]

    @staticmethod
    def extract_sections(text: str) -> List[Tuple[str, str, str]]:
        """Extract numbered sections from contract text."""
        sections = []
        # Pattern: "1. Title" or "Section 1:" or "Article 1."
        pattern = r'(?:^|\n)\s*((?:Section|Article|Clause)?\s*\d+[\.\):]?\s*)([^\n]+)\n((?:(?!(?:Section|Article|Clause)?\s*\d+[\.\):]?\s*[A-Z]).)*)'
        matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
        for num, title, content in matches:
            sections.append((num.strip(), title.strip(), content.strip()[:2000]))
        return sections

    @staticmethod
    def detect_contract_type(text: str) -> str:
        text_lower = text[:5000].lower()
        type_keywords = {
            ContractType.NDA.value: ["non-disclosure", "confidential", "nda", "proprietary information"],
            ContractType.SLA.value: ["service level", "uptime", "sla", "availability"],
            ContractType.MSA.value: ["master service", "msa", "framework agreement"],
            ContractType.EMPLOYMENT.value: ["employment", "employee", "employer", "salary", "termination of employment"],
            ContractType.LICENSE.value: ["license", "licensee", "licensor", "intellectual property", "royalt"],
            ContractType.SAAS.value: ["software as a service", "saas", "subscription", "cloud service"],
        }
        for ctype, keywords in type_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return ctype
        return ContractType.CUSTOM.value

    @staticmethod
    def extract_governing_law(text: str) -> str:
        patterns = [
            r'(?:governed by|governing law|laws of)\s+(?:the\s+)?(?:State of\s+)?([A-Z][A-Za-z\s]+?)(?:\.|,|\n)',
            r'(?:jurisdiction of)\s+([A-Z][A-Za-z\s]+?)(?:\.|,|\n)',
        ]
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return ""


# ── Risk Analyzer ───────────────────────────────────────────────────────────

class RiskAnalyzer:
    """Analyze contract clauses for legal risk indicators."""

    RISK_KEYWORDS = {
        ClauseRisk.CRITICAL: [
            "unlimited liability", "indemnify and hold harmless",
            "sole discretion", "waive all rights", "irrevocable",
            "perpetual license", "no limitation of liability",
        ],
        ClauseRisk.HIGH: [
            "indemnification", "limitation of liability",
            "liquidated damages", "non-compete", "non-solicitation",
            "automatic renewal", "exclusive", "assignable",
            "intellectual property assignment",
        ],
        ClauseRisk.MEDIUM: [
            "termination", "force majeure", "confidentiality",
            "warranty", "dispute resolution", "arbitration",
            "penalty", "breach",
        ],
    }

    OBLIGATION_KEYWORDS = [
        "shall", "must", "agrees to", "is required to",
        "will provide", "is obligated", "undertakes to",
    ]

    @staticmethod
    def assess_clause(title: str, content: str) -> Tuple[ClauseRisk, str, List[str]]:
        text = f"{title} {content}".lower()
        risk = ClauseRisk.LOW
        reason = ""
        obligations = []

        for level in [ClauseRisk.CRITICAL, ClauseRisk.HIGH, ClauseRisk.MEDIUM]:
            for keyword in RiskAnalyzer.RISK_KEYWORDS[level]:
                if keyword in text:
                    risk = level
                    reason = f"Contains '{keyword}'"
                    break
            if risk != ClauseRisk.LOW:
                break

        # Extract obligations
        for sentence in content.split("."):
            sentence = sentence.strip()
            if any(kw in sentence.lower() for kw in RiskAnalyzer.OBLIGATION_KEYWORDS):
                if len(sentence) > 15:
                    obligations.append(sentence[:200])

        return risk, reason, obligations


# ── Contract Comparator ────────────────────────────────────────────────────

class ContractComparator:
    """Compare two contracts to find differences."""

    @staticmethod
    def compare(text_a: str, text_b: str) -> Dict:
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())

        only_a = words_a - words_b
        only_b = words_b - words_a
        common = words_a & words_b
        similarity = len(common) / max(len(words_a | words_b), 1) * 100

        return {
            "similarity_pct": round(similarity, 2),
            "words_only_in_a": len(only_a),
            "words_only_in_b": len(only_b),
            "common_words": len(common),
            "sample_diff_a": list(only_a)[:20],
            "sample_diff_b": list(only_b)[:20],
        }


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniLegalContractEngine:
    """
    OMNI Legal Contract Engine — Zero-Prod Contract Analysis & Risk Assessment.

    Capabilities (all native stdlib — regex NLP):
      - Contract type detection (NDA, SLA, MSA, etc.)
      - Party extraction from legal text
      - Section/clause parsing
      - Risk level assessment (critical/high/medium/low)
      - Obligation extraction
      - Governing law detection
      - Contract comparison/diff
    """

    def __init__(self):
        self.parser = ContractParser()
        self.risk = RiskAnalyzer()
        self.comparator = ContractComparator()

    def analyze(self, text: str) -> ContractAnalysis:
        """Full analysis pipeline on contract text."""
        analysis = ContractAnalysis()

        # Metadata
        analysis.metadata.word_count = len(text.split())
        analysis.metadata.content_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        analysis.metadata.contract_type = self.parser.detect_contract_type(text)
        analysis.metadata.governing_law = self.parser.extract_governing_law(text)
        analysis.metadata.parties = self.parser.extract_parties(text)

        dates = self.parser.extract_dates(text)
        if dates:
            analysis.metadata.effective_date = dates[0]

        # Section analysis
        sections = self.parser.extract_sections(text)
        risk_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for num, title, content in sections:
            risk_level, reason, obligations = self.risk.assess_clause(title, content)
            clause = ContractClause(
                section=num, title=title, content=content[:500],
                risk_level=risk_level, risk_reason=reason,
                obligations=obligations,
            )
            analysis.clauses.append(clause)
            risk_counts[risk_level.value] += 1
            analysis.obligations.extend(obligations)

        analysis.metadata.total_clauses = len(analysis.clauses)
        analysis.risk_summary = risk_counts

        # Warnings
        if risk_counts["critical"] > 0:
            analysis.warnings.append(f"{risk_counts['critical']} CRITICAL risk clause(s) found — legal review required")
        if not analysis.metadata.governing_law:
            analysis.warnings.append("No governing law clause detected")
        if not analysis.metadata.parties:
            analysis.warnings.append("Could not extract contract parties")

        return analysis

    def analyze_file(self, filepath: str) -> Dict:
        """Analyze a contract from a text file."""
        if not os.path.isfile(filepath):
            return {"error": "File not found"}
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        result = self.analyze(text)
        return {
            "file": filepath,
            "type": result.metadata.contract_type,
            "word_count": result.metadata.word_count,
            "clauses": result.metadata.total_clauses,
            "risk_summary": result.risk_summary,
            "obligations": len(result.obligations),
            "warnings": result.warnings,
            "governing_law": result.metadata.governing_law,
            "parties": [{"name": p.name, "role": p.role} for p in result.metadata.parties],
        }

    def compare(self, text_a: str, text_b: str) -> Dict:
        return self.comparator.compare(text_a, text_b)

    def diagnostics(self) -> Dict:
        return {
            "engine": "OmniLegalContractEngine",
            "status": "active",
            "capabilities": ["contract_type_detect", "party_extraction",
                             "clause_parsing", "risk_assessment",
                             "obligation_extraction", "governing_law",
                             "contract_comparison"],
            "supported_types": [t.value for t in ContractType],
        }


if __name__ == "__main__":
    engine = OmniLegalContractEngine()
    print("[LegalContract] Diagnostics:")
    print(json.dumps(engine.diagnostics(), indent=2))
