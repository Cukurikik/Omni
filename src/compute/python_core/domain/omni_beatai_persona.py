#!/usr/bin/env python3
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OMNI BEATAI PERSONA ENGINE — AI Character Simulation & Teaching
# Meta-functionalized from: beatai-org/BeatAI (4.7k★)
# Paradigm: AI persona simulation for interactive learning
# Layer: DOMAIN (Business/Education)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
OMNI BeatAI Persona Engine — Simulate expert AI characters for
interactive teaching, code review, and knowledge transfer.

Key paradigms absorbed:
1. Character Templates — with expertise domains, voice, catchphrases
2. Debate Format — multiple personas argue opposing views
3. Spicy Commentary — engaging, opinionated review style
4. Learning Path Integration — personas guide through curricula
5. Context-Aware Review — analyze code/data with persona lens
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import time
import random
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
from enum import Enum


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 1: Persona Archetypes
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class ExpertiseDomain(Enum):
    SYSTEMS = "systems_engineering"
    AI_ML = "ai_machine_learning"
    ARCHITECTURE = "software_architecture"
    SECURITY = "cybersecurity"
    DATA = "data_science"
    DEVOPS = "devops_sre"
    PRODUCT = "product_management"
    PERFORMANCE = "performance_engineering"
    RESEARCH = "research_science"


class PersonaStyle(Enum):
    ANALYTICAL = "analytical"    # Data-driven, precise
    PROVOCATIVE = "provocative"  # Challenges assumptions
    MENTORING = "mentoring"      # Patient, educational
    PRAGMATIC = "pragmatic"      # Gets to the point
    VISIONARY = "visionary"      # Big-picture thinking


@dataclass
class PersonaTemplate:
    """An AI teaching persona with domain expertise and voice."""
    name: str
    title: str
    expertise: List[ExpertiseDomain]
    style: PersonaStyle
    voice_traits: List[str]        # e.g. ["sarcastic", "data-obsessed"]
    catchphrases: List[str]
    review_patterns: List[str]     # What they look for in code review
    teaching_principles: List[str]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 2: Built-in Personas (inspired by BeatAI's celebrity approach)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BUILTIN_PERSONAS = {
    "architect": PersonaTemplate(
        name="The Architect",
        title="Chief Systems Architect",
        expertise=[ExpertiseDomain.ARCHITECTURE, ExpertiseDomain.SYSTEMS],
        style=PersonaStyle.ANALYTICAL,
        voice_traits=["precise", "pattern-obsessed", "principled"],
        catchphrases=[
            "Architecture is about the decisions you wish you could defer.",
            "If you can't draw it on a whiteboard, you can't build it.",
            "Coupling is the root of all evil, worse than premature optimization."
        ],
        review_patterns=[
            "Check module coupling and cohesion",
            "Validate separation of concerns",
            "Identify SOLID violations",
            "Review error propagation paths",
        ],
        teaching_principles=[
            "Always start with the domain model",
            "Let the architecture emerge from requirements",
            "Prefer composition over inheritance",
        ],
    ),
    "hacker": PersonaTemplate(
        name="The Hacker",
        title="Offensive Security Specialist",
        expertise=[ExpertiseDomain.SECURITY, ExpertiseDomain.SYSTEMS],
        style=PersonaStyle.PROVOCATIVE,
        voice_traits=["paranoid", "blunt", "hacker-mindset"],
        catchphrases=[
            "Trust no input. Validate everything. Assume breach.",
            "Your auth middleware? I bypassed it in 3 lines.",
            "Security isn't a feature. It's the foundation.",
        ],
        review_patterns=[
            "Scan for injection vulnerabilities",
            "Check authentication/authorization gaps",
            "Review secret management",
            "Identify exposed attack surface",
        ],
        teaching_principles=[
            "Think like an attacker first",
            "Defense in depth, always",
            "The weakest link is usually the developer",
        ],
    ),
    "data_wizard": PersonaTemplate(
        name="The Data Wizard",
        title="Chief Data Scientist",
        expertise=[ExpertiseDomain.DATA, ExpertiseDomain.AI_ML],
        style=PersonaStyle.MENTORING,
        voice_traits=["stats-driven", "patient", "hypothesis-first"],
        catchphrases=[
            "In God we trust. All others must bring data.",
            "Correlation doesn't imply causation, but it does waggle its eyebrows.",
            "Your model is only as good as your training data.",
        ],
        review_patterns=[
            "Check for data leakage",
            "Validate train/test split methodology",
            "Review feature engineering rationale",
            "Assess model evaluation metrics",
        ],
        teaching_principles=[
            "Always start with EDA",
            "Simple models first, complexity later",
            "Track every experiment, reproduce every result",
        ],
    ),
    "performance_guru": PersonaTemplate(
        name="The Performance Guru",
        title="Senior Performance Engineer",
        expertise=[ExpertiseDomain.PERFORMANCE, ExpertiseDomain.SYSTEMS],
        style=PersonaStyle.PRAGMATIC,
        voice_traits=["numbers-obsessed", "impatient-with-waste", "benchmark-everything"],
        catchphrases=[
            "If you haven't measured it, you can't improve it.",
            "That O(n^2) loop? I can smell it from here.",
            "Premature optimization is bad. Late optimization is worse.",
        ],
        review_patterns=[
            "Profile big-O complexity of hot paths",
            "Check memory allocation patterns",
            "Identify unnecessary copies and allocations",
            "Review caching opportunities",
        ],
        teaching_principles=[
            "Measure first, optimize second",
            "Know your hardware (cache lines, SIMD, branch prediction)",
            "Batch operations trump single operations",
        ],
    ),
    "visionary": PersonaTemplate(
        name="The Visionary",
        title="Chief Innovation Officer",
        expertise=[ExpertiseDomain.PRODUCT, ExpertiseDomain.RESEARCH],
        style=PersonaStyle.VISIONARY,
        voice_traits=["inspiring", "big-picture", "future-focused"],
        catchphrases=[
            "We're not building software. We're building the future.",
            "The best product is the one that makes itself obsolete.",
            "Think 10x, not 10%.",
        ],
        review_patterns=[
            "Assess market impact and user value",
            "Identify scalability ceiling",
            "Review feature extensibility",
            "Check competitive differentiation",
        ],
        teaching_principles=[
            "Start with the user problem, not the technology",
            "Build for tomorrow's scale today",
            "Innovation is saying no to 1000 things",
        ],
    ),
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 3: Review & Commentary Engine
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@dataclass
class ReviewComment:
    """A single review comment from a persona."""
    persona_name: str
    category: str       # e.g. "security", "performance", "architecture"
    severity: str       # "critical", "warning", "suggestion", "praise"
    comment: str
    line_ref: Optional[str] = None
    catchphrase: Optional[str] = None


class PersonaReviewer:
    """Generates code/architecture reviews from a persona's perspective."""

    def __init__(self, persona: PersonaTemplate):
        self.persona = persona

    def review_code(self, code: str, filename: str = "") -> List[ReviewComment]:
        """Review code from this persona's perspective."""
        comments = []
        lines = code.split("\n")

        # Check persona-specific patterns
        for pattern in self.persona.review_patterns:
            # Each persona has domain-specific checks
            comment = ReviewComment(
                persona_name=self.persona.name,
                category=self.persona.expertise[0].value if self.persona.expertise else "general",
                severity="suggestion",
                comment=f"[{pattern}] — Consider reviewing this aspect.",
                catchphrase=random.choice(self.persona.catchphrases) if self.persona.catchphrases else None,
            )
            comments.append(comment)

        # Code-specific heuristics
        for i, line in enumerate(lines):
            stripped = line.strip()
            if "except:" in stripped or "except Exception" in stripped:
                comments.append(ReviewComment(
                    self.persona.name, "error_handling", "warning",
                    f"Line {i+1}: Bare except clause — catch specific exceptions.",
                    line_ref=f"L{i+1}",
                ))
            if "eval(" in stripped or "exec(" in stripped:
                comments.append(ReviewComment(
                    self.persona.name, "security", "critical",
                    f"Line {i+1}: eval/exec detected — major injection risk!",
                    line_ref=f"L{i+1}",
                ))
            if "TODO" in stripped or "FIXME" in stripped:
                comments.append(ReviewComment(
                    self.persona.name, "quality", "suggestion",
                    f"Line {i+1}: Unresolved TODO/FIXME in production code.",
                    line_ref=f"L{i+1}",
                ))
            if len(stripped) > 120:
                comments.append(ReviewComment(
                    self.persona.name, "readability", "suggestion",
                    f"Line {i+1}: Line exceeds 120 chars — consider refactoring.",
                    line_ref=f"L{i+1}",
                ))

        return comments

    def generate_lesson(self, topic: str) -> Dict:
        """Generate a teaching lesson from this persona's perspective."""
        return {
            "instructor": self.persona.name,
            "title": self.persona.title,
            "topic": topic,
            "style": self.persona.style.value,
            "principles": self.persona.teaching_principles,
            "opening": random.choice(self.persona.catchphrases),
            "review_focus": self.persona.review_patterns,
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 4: Debate Engine (Multi-Persona Discussion)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class DebateEngine:
    """
    Orchestrates multi-persona debates on technical topics.
    Each persona argues from their domain expertise.
    """

    def __init__(self, topic: str, personas: Optional[List[str]] = None):
        self.topic = topic
        self.persona_names = personas or list(BUILTIN_PERSONAS.keys())
        self.personas = [BUILTIN_PERSONAS[n] for n in self.persona_names if n in BUILTIN_PERSONAS]
        self.arguments: List[Dict] = []

    def debate(self) -> List[Dict]:
        """Generate debate arguments from each persona."""
        for persona in self.personas:
            argument = {
                "speaker": persona.name,
                "title": persona.title,
                "style": persona.style.value,
                "position": f"From {persona.expertise[0].value}: {self.topic}",
                "key_points": persona.teaching_principles[:2],
                "opener": random.choice(persona.catchphrases),
                "review_lens": persona.review_patterns[:2],
            }
            self.arguments.append(argument)
        return self.arguments

    def summary(self) -> str:
        """Summarize the debate."""
        lines = [f"Debate: {self.topic}", "=" * 50]
        for arg in self.arguments:
            lines.append(f"\n  {arg['speaker']} ({arg['title']}):")
            lines.append(f"    \"{arg['opener']}\"")
            for point in arg['key_points']:
                lines.append(f"    • {point}")
        return "\n".join(lines)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 5: Main Persona Engine
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class OmniBeatAIEngine:
    """
    The OMNI BeatAI Engine — AI persona simulation for learning.
    Manages a roster of expert personas, conducts reviews, debates,
    and generates personalized learning paths.
    """

    def __init__(self):
        self.personas: Dict[str, PersonaTemplate] = dict(BUILTIN_PERSONAS)
        self.reviewers: Dict[str, PersonaReviewer] = {
            name: PersonaReviewer(p) for name, p in self.personas.items()
        }

    def add_persona(self, key: str, persona: PersonaTemplate):
        self.personas[key] = persona
        self.reviewers[key] = PersonaReviewer(persona)

    def review(self, code: str, persona_keys: Optional[List[str]] = None) -> List[ReviewComment]:
        """Multi-persona code review."""
        keys = persona_keys or list(self.reviewers.keys())
        all_comments = []
        for key in keys:
            reviewer = self.reviewers.get(key)
            if reviewer:
                comments = reviewer.review_code(code)
                all_comments.extend(comments)
        return all_comments

    def debate(self, topic: str, persona_keys: Optional[List[str]] = None) -> str:
        engine = DebateEngine(topic, persona_keys)
        engine.debate()
        return engine.summary()

    def get_lesson(self, persona_key: str, topic: str) -> Dict:
        reviewer = self.reviewers.get(persona_key)
        if reviewer:
            return reviewer.generate_lesson(topic)
        return {"error": f"Persona '{persona_key}' not found"}

    def list_personas(self) -> List[Dict]:
        return [
            {"key": k, "name": p.name, "title": p.title,
             "expertise": [e.value for e in p.expertise],
             "style": p.style.value}
            for k, p in self.personas.items()
        ]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# META-FUNCTION TEST
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    print("=" * 70)
    print("  OMNI BEATAI PERSONA ENGINE")
    print("=" * 70)

    engine = OmniBeatAIEngine()

    # List personas
    personas = engine.list_personas()
    print(f"\n   Personas loaded: {len(personas)}")
    for p in personas:
        print(f"      {p['name']:25s} ({p['style']:15s}) — {', '.join(p['expertise'][:2])}")

    # Multi-persona code review
    sample_code = '''
def process_data(data):
    try:
        result = eval(data["expression"])  # TODO: fix this
        return result
    except:
        return None
'''
    comments = engine.review(sample_code, ["architect", "hacker"])
    print(f"\n   Code Review: {len(comments)} comments")
    for c in comments:
        print(f"      [{c.severity:10s}] {c.persona_name}: {c.comment[:60]}")

    # Debate
    debate = engine.debate("Should we use microservices or monolith?",
                           ["architect", "performance_guru", "visionary"])
    print(f"\n{debate}")

    # Lesson
    lesson = engine.get_lesson("data_wizard", "Feature Engineering Best Practices")
    print(f"\n   Lesson: {lesson.get('topic')}")
    print(f"   Instructor: {lesson.get('instructor')}")
    print(f"   Opening: \"{lesson.get('opening')}\"")

    print("\n" + "=" * 70)
    print("  META-FUNCTIONALIZED: BeatAI Persona Engine")
    print("   5 built-in expert personas (Architect/Hacker/Data/Perf/Visionary)")
    print("   Multi-persona code review with severity-rated comments")
    print("   Debate engine for multi-perspective discussions")
    print("   Lesson generation with teaching principles")
    print("   Extensible persona registry")
    print("=" * 70)
