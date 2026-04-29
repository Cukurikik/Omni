ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI AGENT SKILLS ENGINE — Dynamic Skill Catalog & On-Demand Loader
# ===========================================================================
# Source Paradigm: https://github.com/heilcheng/awesome-agent-skills
# Domain Layer  : AI Agents
# Zero-Prod     : 100% Native — os, json, hashlib, real file I/O
# ===========================================================================
"""
awesome-agent-skills teaches us:
  1. SKILL.md format: portable on-demand capabilities for AI agents
  2. Skill categories: coding, research, security, infrastructure, creative
  3. Context-efficient loading: only load skills when needed
  4. No retraining: equip agents with new abilities via markdown recipes
  5. Cross-platform: works with Claude, Copilot, Cursor, Gemini, Codex
  6. Community-driven skill registry

This engine distills those paradigms into OMNI-native Python for
managing, indexing, and dynamically loading agent skill definitions.
"""

import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


# ── Data Models ──────────────────────────────────────────────────────────────

@dataclass
class AgentSkill:
    name: str
    category: str
    description: str
    file_path: str
    content: str = ""
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    content_hash: str = ""
    loaded: bool = False


@dataclass
class SkillCategory:
    name: str
    description: str
    skills: List[str] = field(default_factory=list)


# ── Built-In Skill Definitions ──────────────────────────────────────────────

BUILTIN_SKILLS: Dict[str, Dict] = {
    "code_review": {
        "category": "development",
        "description": "Perform thorough code review with security, performance, and maintainability checks",
        "tags": ["coding", "review", "quality"],
        "content": """# Code Review Skill
## Instructions
1. Analyze the code for security vulnerabilities (SQL injection, XSS, CSRF)
2. Check for performance anti-patterns (N+1 queries, unnecessary allocations)
3. Evaluate error handling (monadic Result types preferred over try/catch)
4. Verify naming conventions and documentation completeness
5. Suggest refactoring opportunities using SOLID principles
6. Check for proper input validation and sanitization
## Output Format
Produce a structured review with: severity, location, description, suggestion
""",
    },
    "bug_diagnosis": {
        "category": "development",
        "description": "Systematic bug diagnosis using stack trace analysis and bisection",
        "tags": ["debugging", "diagnosis", "fix"],
        "content": """# Bug Diagnosis Skill
## Instructions
1. Read the error/stack trace and identify the origin layer
2. Check for domain layer segregation violations
3. Verify monadic error handling compliance
4. Test with minimal reproduction case
5. Identify root cause vs symptoms
6. Provide fix with explanation of WHY the bug occurred
7. Suggest preventive refactoring
""",
    },
    "api_design": {
        "category": "development",
        "description": "Design RESTful or GraphQL APIs following best practices",
        "tags": ["api", "rest", "graphql", "design"],
        "content": """# API Design Skill
## Instructions
1. Define resource models with proper naming (plural nouns, kebab-case)
2. Design endpoints following REST conventions (GET/POST/PUT/DELETE)
3. Implement proper HTTP status codes (201 Created, 404 Not Found, etc.)
4. Add pagination, filtering, and sorting parameters
5. Design error response format with error codes
6. Version the API (v1, v2) in the URL path
7. Document with OpenAPI/Swagger specification
""",
    },
    "security_audit": {
        "category": "security",
        "description": "Perform comprehensive security audit on codebases and infrastructure",
        "tags": ["security", "audit", "vulnerability"],
        "content": """# Security Audit Skill
## Instructions
1. Scan for embedded secrets (API keys, passwords, tokens)
2. Check authentication and authorization mechanisms
3. Verify input validation on all external-facing endpoints
4. Audit dependency versions for known CVEs
5. Check for proper HTTPS/TLS configuration
6. Verify CORS and CSP headers
7. Test for common OWASP Top 10 vulnerabilities
8. Review logging for sensitive data exposure
""",
    },
    "data_extraction": {
        "category": "research",
        "description": "Extract and structure data from web pages, documents, and APIs",
        "tags": ["scraping", "extraction", "data"],
        "content": """# Data Extraction Skill
## Instructions
1. Identify the data source type (HTML, JSON API, PDF, CSV)
2. For web pages: parse DOM structure, extract text and links
3. For APIs: handle pagination, rate limiting, authentication
4. Normalize extracted data into structured format (JSON/CSV)
5. Validate data integrity (types, ranges, completeness)
6. Handle encoding issues (UTF-8, ISO-8859-1)
7. Implement retry logic for transient failures
""",
    },
    "cloud_architecture": {
        "category": "infrastructure",
        "description": "Design cloud-native architectures on GCP, AWS, or Azure",
        "tags": ["cloud", "architecture", "infrastructure"],
        "content": """# Cloud Architecture Skill
## Instructions
1. Identify workload characteristics (stateless, stateful, event-driven)
2. Select appropriate compute services (Cloud Run, GKE, Lambda)
3. Design data layer (Firestore, BigQuery, Cloud SQL)
4. Implement messaging (Pub/Sub, EventArc) for decoupling
5. Configure IAM with least-privilege principle
6. Set up monitoring (Cloud Monitoring, Logging, Trace)
7. Design for high availability (multi-region, auto-scaling)
8. Estimate costs and set budget alerts
""",
    },
    "document_generation": {
        "category": "creative",
        "description": "Generate professional documents (reports, proposals, specifications)",
        "tags": ["document", "writing", "report"],
        "content": """# Document Generation Skill
## Instructions
1. Identify document type and audience
2. Create proper heading hierarchy (H1 for title, H2 for sections)
3. Include executive summary for long documents
4. Use tables for structured data comparisons
5. Add code blocks with language specification
6. Include diagrams (Mermaid) for architecture/flow
7. Proofread for clarity, conciseness, and correctness
""",
    },
    "ci_cd_pipeline": {
        "category": "infrastructure",
        "description": "Design and implement CI/CD pipelines for automated build/test/deploy",
        "tags": ["ci", "cd", "devops", "automation"],
        "content": """# CI/CD Pipeline Skill
## Instructions
1. Define stages: lint → build → test → security scan → deploy
2. Configure environment-based branching (dev, staging, prod)
3. Implement artifact caching for faster builds
4. Add secret management (env vars, secret manager)
5. Configure deployment strategies (blue-green, canary, rolling)
6. Set up notifications (Slack, email) for failures
7. Implement rollback procedures
8. Add performance/load testing gate
""",
    },
}


# ── Skill Scanner ───────────────────────────────────────────────────────────

class SkillScanner:
    """Scan directories for SKILL.md files and custom skill definitions."""

    @staticmethod
    def scan_directory(path: str) -> List[AgentSkill]:
        """Find all SKILL.md files in a directory tree."""
        skills = []
        if not os.path.isdir(path):
            return skills

        for root, dirs, files in os.walk(path):
            for f in files:
                if f.upper() == "SKILL.MD":
                    full = os.path.join(root, f)
                    skill_name = os.path.basename(root).replace("-", "_").lower()
                    try:
                        with open(full, "r", encoding="utf-8") as fh:
                            content = fh.read()
                        skills.append(AgentSkill(
                            name=skill_name,
                            category=SkillScanner._infer_category(content),
                            description=SkillScanner._extract_description(content),
                            file_path=full,
                            content=content,
                            content_hash=hashlib.sha256(content.encode()).hexdigest()[:16],
                            loaded=True,
                        ))
                    except Exception:
                        pass
        return skills

    @staticmethod
    def _infer_category(content: str) -> str:
        content_lower = content.lower()
        if any(k in content_lower for k in ["security", "audit", "vulnerability"]):
            return "security"
        if any(k in content_lower for k in ["cloud", "deploy", "infrastructure", "kubernetes"]):
            return "infrastructure"
        if any(k in content_lower for k in ["test", "debug", "review", "code"]):
            return "development"
        if any(k in content_lower for k in ["data", "scrape", "extract", "research"]):
            return "research"
        return "general"

    @staticmethod
    def _extract_description(content: str) -> str:
        """Extract first meaningful line as description."""
        for line in content.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and len(stripped) > 10:
                return stripped[:200]
        return ""


# ── Skill Registry ──────────────────────────────────────────────────────────

class SkillRegistry:
    """Central registry for all agent skills (builtin + filesystem)."""

    def __init__(self):
        self.skills: Dict[str, AgentSkill] = {}
        self._load_builtins()

    def _load_builtins(self):
        """Load all built-in skill definitions."""
        for name, spec in BUILTIN_SKILLS.items():
            self.skills[name] = AgentSkill(
                name=name,
                category=spec["category"],
                description=spec["description"],
                file_path="<builtin>",
                content=spec["content"],
                tags=spec.get("tags", []),
                content_hash=hashlib.sha256(spec["content"].encode()).hexdigest()[:16],
                loaded=True,
            )

    def register_from_directory(self, path: str) -> int:
        """Scan a directory and register discovered skills."""
        found = SkillScanner.scan_directory(path)
        for skill in found:
            self.skills[skill.name] = skill
        return len(found)

    def get(self, name: str) -> Optional[AgentSkill]:
        return self.skills.get(name)

    def search(self, query: str) -> List[AgentSkill]:
        """Search skills by name, description, or tags."""
        query_lower = query.lower()
        results = []
        for skill in self.skills.values():
            if (query_lower in skill.name.lower() or
                query_lower in skill.description.lower() or
                any(query_lower in t for t in skill.tags)):
                results.append(skill)
        return results

    def list_by_category(self) -> Dict[str, List[str]]:
        """Group skills by category."""
        categories: Dict[str, List[str]] = {}
        for skill in self.skills.values():
            categories.setdefault(skill.category, []).append(skill.name)
        return categories

    def export_catalog(self) -> List[Dict]:
        """Export full skill catalog as list of dicts."""
        return [
            {
                "name": s.name, "category": s.category,
                "description": s.description, "tags": s.tags,
                "hash": s.content_hash, "source": s.file_path,
            }
            for s in sorted(self.skills.values(), key=lambda x: x.category)
        ]


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniAgentSkillsEngine:
    """
    OMNI Agent Skills Engine — Zero-Prod Dynamic Skill Catalog & Loader.

    Capabilities (all native stdlib):
      - Built-in skill library (8 production skills)
      - Filesystem SKILL.md scanner
      - Skill search by name/description/tags
      - Category-based skill organization
      - Content hashing for version tracking
      - JSON catalog export
    """

    def __init__(self):
        self.registry = SkillRegistry()

    def load_skills_from(self, directory: str) -> Dict:
        """Load additional skills from a directory."""
        count = self.registry.register_from_directory(directory)
        return {"loaded": count, "total": len(self.registry.skills)}

    def get_skill(self, name: str) -> Optional[Dict]:
        """Get a specific skill's full content."""
        skill = self.registry.get(name)
        if skill:
            return {
                "name": skill.name, "category": skill.category,
                "description": skill.description, "content": skill.content,
                "tags": skill.tags, "hash": skill.content_hash,
            }
        return None

    def search(self, query: str) -> List[Dict]:
        """Search skills matching a query."""
        results = self.registry.search(query)
        return [{"name": s.name, "category": s.category, "description": s.description} for s in results]

    def catalog(self) -> Dict:
        """Get full skill catalog organized by category."""
        return {
            "total_skills": len(self.registry.skills),
            "categories": self.registry.list_by_category(),
            "skills": self.registry.export_catalog(),
        }

    def diagnostics(self) -> Dict:
        cats = self.registry.list_by_category()
        return {
            "engine": "OmniAgentSkillsEngine",
            "status": "active",
            "total_skills": len(self.registry.skills),
            "categories": {k: len(v) for k, v in cats.items()},
            "capabilities": ["builtin_skills", "filesystem_scan", "skill_search",
                             "category_index", "content_hash", "json_export"],
        }


if __name__ == "__main__":
    engine = OmniAgentSkillsEngine()
    print("[AgentSkills] Catalog:")
    print(json.dumps(engine.diagnostics(), indent=2))
