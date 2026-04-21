ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI JOB OPS ENGINE — Job Application Pipeline & Tracker
# ===========================================================================
# Source Paradigm: https://github.com/DaKheera47/job-ops
# Domain Layer  : Domain (Job Application Management)
# Zero-Mock     : 100% Native — sqlite3, json, os, hashlib, re
# ===========================================================================
"""
job-ops teaches us:
  1. Job application pipeline tracking (Kanban-style stages)
  2. Resume version management per application
  3. Job description snapshotting
  4. Multi-board aggregation (LinkedIn, Indeed, Glassdoor)
  5. Application status tracking (applied, interview, offer, rejected)
  6. Local-first, privacy-focused data storage (SQLite)

This engine distills those paradigms into OMNI-native Python for
comprehensive job application lifecycle management.
"""

import hashlib
import json
import os
import re
import sqlite3
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


# ── Data Models ──────────────────────────────────────────────────────────────

class ApplicationStage(Enum):
    DISCOVERED = "discovered"
    BOOKMARKED = "bookmarked"
    TAILORING = "tailoring"
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW = "interview"
    ASSESSMENT = "assessment"
    OFFER = "offer"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class JobSource(Enum):
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    GLASSDOOR = "glassdoor"
    COMPANY = "company_site"
    REFERRAL = "referral"
    OTHER = "other"


@dataclass
class JobListing:
    job_id: str
    title: str
    company: str
    location: str = ""
    salary_range: str = ""
    source: JobSource = JobSource.OTHER
    url: str = ""
    description: str = ""
    requirements: List[str] = field(default_factory=list)
    posted_date: str = ""
    deadline: str = ""


@dataclass
class Application:
    app_id: str
    job: JobListing
    stage: ApplicationStage = ApplicationStage.DISCOVERED
    resume_version: str = ""
    cover_letter: str = ""
    applied_date: str = ""
    notes: str = ""
    follow_up_date: str = ""
    interviews: List[Dict] = field(default_factory=list)
    created_at: float = 0
    updated_at: float = 0


# ── Job Description Analyzer ──────────────────────────────────────────────

class JDAnalyzer:
    """Extract structured information from job descriptions."""

    SKILL_PATTERNS = {
        "python": r'\bpython\b', "javascript": r'\bjavascript\b',
        "typescript": r'\btypescript\b', "react": r'\breact\b',
        "nodejs": r'\bnode\.?js\b', "java": r'\bjava\b',
        "kubernetes": r'\bkubernetes\b|\bk8s\b', "docker": r'\bdocker\b',
        "aws": r'\baws\b', "gcp": r'\bgcp\b|\bgoogle cloud\b',
        "sql": r'\bsql\b', "golang": r'\bgo(lang)?\b',
        "rust": r'\brust\b', "machine_learning": r'\bmachine learning\b|\bml\b',
        "ai": r'\bartificial intelligence\b|\bai\b',
        "devops": r'\bdevops\b', "ci_cd": r'\bci/?cd\b',
        "agile": r'\bagile\b|\bscrum\b',
    }

    @staticmethod
    def extract_skills(description: str) -> List[str]:
        found = []
        for skill, pattern in JDAnalyzer.SKILL_PATTERNS.items():
            if re.search(pattern, description, re.IGNORECASE):
                found.append(skill)
        return sorted(found)

    @staticmethod
    def extract_experience(description: str) -> Optional[str]:
        match = re.search(r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)', description, re.I)
        return f"{match.group(1)}+ years" if match else None

    @staticmethod
    def extract_education(description: str) -> Optional[str]:
        patterns = [
            r"bachelor'?s?\s+(?:degree)?", r"master'?s?\s+(?:degree)?",
            r"ph\.?d\.?", r"b\.?s\.?\s+in", r"m\.?s\.?\s+in",
        ]
        for p in patterns:
            if re.search(p, description, re.I):
                match = re.search(p, description, re.I)
                return match.group(0).strip()
        return None

    @staticmethod
    def analyze(description: str) -> Dict:
        return {
            "skills": JDAnalyzer.extract_skills(description),
            "experience": JDAnalyzer.extract_experience(description),
            "education": JDAnalyzer.extract_education(description),
            "word_count": len(description.split()),
            "has_salary": bool(re.search(r'\$[\d,]+|\d+k', description, re.I)),
            "is_remote": bool(re.search(r'\bremote\b|\bhybrid\b|\bwork from home\b', description, re.I)),
        }


# ── Application Database (SQLite) ─────────────────────────────────────────

class ApplicationDB:
    """Persistent job application tracking."""

    def __init__(self, db_path: str = ""):
        if not db_path:
            try:
                db_path = os.path.join(os.path.dirname(__file__), "..", ".job_ops.db")
            except NameError:
                db_path = os.path.join(os.getcwd(), ".job_ops.db")
        self.db_path = db_path
        self._init()

    def _init(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                app_id TEXT PRIMARY KEY,
                title TEXT, company TEXT, location TEXT,
                source TEXT, url TEXT, stage TEXT,
                resume_version TEXT, notes TEXT,
                skills TEXT, description TEXT,
                created_at REAL, updated_at REAL
            )
        """)
        conn.commit()
        conn.close()

    def upsert(self, app: Application):
        skills = JDAnalyzer.extract_skills(app.job.description)
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """INSERT OR REPLACE INTO applications VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (app.app_id, app.job.title, app.job.company, app.job.location,
             app.job.source.value, app.job.url, app.stage.value,
             app.resume_version, app.notes,
             json.dumps(skills), app.job.description[:5000],
             app.created_at, time.time()),
        )
        conn.commit()
        conn.close()

    def update_stage(self, app_id: str, stage: ApplicationStage):
        conn = sqlite3.connect(self.db_path)
        conn.execute("UPDATE applications SET stage=?, updated_at=? WHERE app_id=?",
                      (stage.value, time.time(), app_id))
        conn.commit()
        conn.close()

    def get_pipeline(self) -> Dict[str, int]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT stage, COUNT(*) FROM applications GROUP BY stage")
        pipeline = {r[0]: r[1] for r in c.fetchall()}
        conn.close()
        return pipeline

    def search(self, query: str) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "SELECT app_id, title, company, stage, skills FROM applications WHERE title LIKE ? OR company LIKE ?",
            (f"%{query}%", f"%{query}%"),
        )
        cols = ["app_id", "title", "company", "stage", "skills"]
        results = [dict(zip(cols, row)) for row in c.fetchall()]
        conn.close()
        return results

    def stats(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM applications")
        total = c.fetchone()[0]
        pipeline = self.get_pipeline()
        conn.close()
        return {"total": total, "pipeline": pipeline}


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniJobOpsEngine:
    """
    OMNI JobOps Engine — Zero-Mock Job Application Pipeline Tracker.

    Capabilities (all native stdlib):
      - Job description NLP analysis (skills, experience, education)
      - Application pipeline tracking (Kanban stages)
      - Resume version management
      - SQLite persistence with search
      - Pipeline statistics and reporting
    """

    def __init__(self):
        self.analyzer = JDAnalyzer()
        self.db = ApplicationDB()

    def add_application(self, title: str, company: str, description: str = "",
                         source: str = "other", url: str = "") -> Dict:
        app_id = hashlib.sha256(f"{title}{company}{time.time()}".encode()).hexdigest()[:12]
        job = JobListing(
            job_id=app_id, title=title, company=company,
            description=description,
            source=JobSource(source) if source in [s.value for s in JobSource] else JobSource.OTHER,
            url=url,
        )
        app = Application(app_id=app_id, job=job, created_at=time.time())
        self.db.upsert(app)
        analysis = self.analyzer.analyze(description) if description else {}
        return {"app_id": app_id, "title": title, "company": company, "analysis": analysis}

    def update_stage(self, app_id: str, stage: str) -> Dict:
        try:
            s = ApplicationStage(stage)
            self.db.update_stage(app_id, s)
            return {"updated": app_id, "stage": stage}
        except ValueError:
            return {"error": f"Invalid stage: {stage}"}

    def get_pipeline(self) -> Dict:
        return self.db.get_pipeline()

    def diagnostics(self) -> Dict:
        return {
            "engine": "OmniJobOpsEngine",
            "status": "active",
            "db_stats": self.db.stats(),
            "capabilities": ["jd_analysis", "skill_extraction", "pipeline_track",
                             "resume_versioning", "sqlite_search", "stage_kanban"],
            "stages": [s.value for s in ApplicationStage],
        }


if __name__ == "__main__":
    engine = OmniJobOpsEngine()
    r = engine.add_application(
        "Senior Python Engineer", "OMNI Corp",
        "We need 5+ years of experience in Python, Docker, Kubernetes, "
        "and machine learning. Remote position. Salary $150k-$200k.",
    )
    print(json.dumps(r, indent=2))
