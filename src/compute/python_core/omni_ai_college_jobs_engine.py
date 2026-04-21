"""
OMNI AI College Jobs Engine
===========================
Production-grade abstraction inspired by speedyapply/2026-AI-College-Jobs.
Provides algorithmic resume parsing and probabilistic candidate matching
against AI taxonomy roles (ML Engineer, Data Scientist, AI Researcher).

OMNI Layer: compute (Python)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------


ENGINE_VERSION = "1.0.0-omni"

class AICollegeJobsError(Exception):
    """Base error for AI College Jobs engine."""

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
# 2. MODELS & TAXONOMY
# ---------------------------------------------------------------------------

@dataclass
class JobRole:
    """Production-grade Job Role component."""
    title: str
    required_keywords: List[str]
    nice_to_have_keywords: List[str]
    base_weight: float = 1.0

@dataclass
class CandidateProfile:
    """Production-grade Candidate Profile component."""
    id: str
    extracted_text: str
    matched_skills: List[str] = field(default_factory=list)
    role_scores: Dict[str, float] = field(default_factory=dict)


class ResumeParser:
    """Parses raw text and extracts canonical AI skills."""
    
    def __init__(self, skill_universe: List[str]):
        """Initialize ResumeParser."""
        self.skill_universe = [s.lower() for s in skill_universe]
        
    def parse(self, raw_text: str) -> Result:
        """Execute parse operation for ResumeParser."""
        if not raw_text or not str(raw_text).strip():
            return Err("Empty or invalid resume text.")
            
        text_lower = raw_text.lower()
        matched = []
        for skill in self.skill_universe:
            # Word boundary regex to avoid partial matches (e.g. 'c' in 'cat')
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                matched.append(skill)
                
        return Ok(matched)


class RoleMatcher:
    """Calculates compatibility score between candidate skills and job requirements."""
    
    def __init__(self, roles: List[JobRole]):
        """Initialize RoleMatcher."""
        self.roles = {role.title: role for role in roles}
        
    def score_candidate(self, candidate_skills: List[str]) -> Result:
        """Compute score for score candidate."""
        if not candidate_skills:
            return Err("Candidate has no extracted skills to evaluate.")
            
        cand_set = set(candidate_skills)
        scores = {}
        
        for title, role in self.roles.items():
            req_set = set(k.lower() for k in role.required_keywords)
            nice_set = set(k.lower() for k in role.nice_to_have_keywords)
            
            # Base logic: required matching
            if req_set:
                req_match = len(cand_set.intersection(req_set)) / len(req_set)
            else:
                req_match = 1.0
                
            # Bonus logic: nice-to-have matching
            if nice_set:
                bonus_match = len(cand_set.intersection(nice_set)) / len(nice_set)
            else:
                bonus_match = 0.0
                
            # Weighted formula
            score = (req_match * 0.8) + (bonus_match * 0.2)
            scores[title] = round(score * role.base_weight * 100, 2)
            
        return Ok(scores)


# ---------------------------------------------------------------------------
# 3. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniAICollegeJobsEngine:
    """
    Production Engine for AI Job Candidate Matching.
    """
    VERSION = "1.0.0"
    ENGINE_ID = "omni-ai-college-jobs"

    def __init__(self):
        # Default AI Domain skill universe
        """Initialize OmniAICollegeJobsEngine."""
        self.skill_universe = [
            "python", "pytorch", "tensorflow", "scikit-learn", "numpy", 
            "pandas", "sql", "aws", "gcp", "docker", "kubernetes", 
            "llm", "nlp", "computer vision", "git", "c++", "rust",
            "fastapi", "flask", "django", "mlops"
        ]
        
        # Default AI roles
        self.default_roles = [
            JobRole(
                title="ML Engineer", 
                required_keywords=["python", "pytorch", "docker", "mlops"],
                nice_to_have_keywords=["kubernetes", "aws", "gcp", "fastapi"]
            ),
            JobRole(
                title="Data Scientist", 
                required_keywords=["python", "pandas", "scikit-learn", "sql"],
                nice_to_have_keywords=["tensorflow", "numpy", "aws"]
            ),
            JobRole(
                title="AI Researcher", 
                required_keywords=["python", "pytorch", "llm", "nlp"],
                nice_to_have_keywords=["c++", "rust", "tensorflow", "computer vision"]
            )
        ]
        
    def get_parser(self) -> ResumeParser:
        """Performs get parser operation for OmniAICollegeJobsEngine."""
        return ResumeParser(self.skill_universe)
        
    def get_matcher(self) -> RoleMatcher:
        """Performs get matcher operation for OmniAICollegeJobsEngine."""
        return RoleMatcher(self.default_roles)

    def evaluate_candidate(self, candidate_id: str, raw_text: str) -> Result:
        """Performs evaluate candidate operation for OmniAICollegeJobsEngine."""
        parser = self.get_parser()
        parse_res = parser.parse(raw_text)
        if isinstance(parse_res, Err):
            return parse_res
            
        skills = parse_res.value
        matcher = self.get_matcher()
        score_res = matcher.score_candidate(skills)
        if isinstance(score_res, Err):
            return score_res
            
        scores = score_res.value
        profile = CandidateProfile(
            id=candidate_id, 
            extracted_text=raw_text, 
            matched_skills=skills, 
            role_scores=scores
        )
        return Ok(profile)

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniAICollegeJobsEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "roles_configured": len(self.default_roles),
            "skills_tracked": len(self.skill_universe),
            "status": "operational",
        }
