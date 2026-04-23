ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI URLWATCH ENGINE — URL Change Monitoring & Diff Detection
# ===========================================================================
# Source Paradigm: https://github.com/thp/urlwatch
# Domain Layer  : Network (Web Monitoring)
# Zero-Prod     : 100% Native — urllib, hashlib, sqlite3, difflib, re
# ===========================================================================
"""
urlwatch teaches us:
  1. Periodic URL monitoring for content changes
  2. Diff-based change detection (unified diff)
  3. Filter pipelines (css, xpath, strip, grep)
  4. Alert channels (email, slack, webhook)
  5. Content hashing for fast duplicate detection
  6. YAML-based job configuration

This engine distills those paradigms into OMNI-native Python for
production URL monitoring with real HTTP fetching and SQLite history.
"""

import difflib
import hashlib
import json
import os
import re
import sqlite3
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


# ── Data Models ──────────────────────────────────────────────────────────────

class ChangeType(Enum):
    NEW = "new"
    CHANGED = "changed"
    UNCHANGED = "unchanged"
    ERROR = "error"


@dataclass
class WatchJob:
    url: str
    name: str = ""
    filter_css: str = ""        # CSS-like content filter
    filter_regex: str = ""      # regex filter
    strip_html: bool = True
    interval_seconds: int = 3600
    headers: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True


@dataclass
class WatchResult:
    url: str
    name: str = ""
    status_code: int = 0
    content_hash: str = ""
    content_length: int = 0
    change_type: ChangeType = ChangeType.NEW
    diff_lines: List[str] = field(default_factory=list)
    diff_stats: Dict[str, int] = field(default_factory=dict)
    fetched_at: float = 0
    error: str = ""


# ── Content Fetcher ────────────────────────────────────────────────────────

class ContentFetcher:
    """Fetch web content with configurable headers."""

    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (OMNI-URLWatch/1.0)",
        "Accept": "text/html,application/xhtml+xml,application/json,text/plain",
    }

    @staticmethod
    def fetch(url: str, headers: Dict = None, timeout: float = 15) -> Tuple[int, str, str]:
        """Fetch URL content. Returns (status_code, content, error)."""
        hdrs = {**ContentFetcher.DEFAULT_HEADERS, **(headers or {})}
        req = urllib.request.Request(url, headers=hdrs)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
                encoding = resp.headers.get_content_charset() or "utf-8"
                content = raw.decode(encoding, errors="replace")
                return resp.getcode(), content, ""
        except urllib.error.HTTPError as e:
            return e.code, "", f"HTTP {e.code}: {e.reason}"
        except urllib.error.URLError as e:
            return 0, "", f"URL Error: {str(e.reason)[:128]}"
        except Exception as e:
            return 0, "", str(e)[:256]


# ── Content Filters ────────────────────────────────────────────────────────

class ContentFilter:
    """Apply filter pipeline to raw content."""

    @staticmethod
    def strip_html(content: str) -> str:
        """Remove HTML tags, keeping text only."""
        text = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    def grep(content: str, pattern: str) -> str:
        """Filter lines matching a regex pattern."""
        lines = content.split("\n")
        matched = [l for l in lines if re.search(pattern, l)]
        return "\n".join(matched)

    @staticmethod
    def extract_between(content: str, start_tag: str, end_tag: str) -> str:
        """Extract content between two markers."""
        s = content.find(start_tag)
        if s == -1:
            return ""
        s += len(start_tag)
        e = content.find(end_tag, s)
        return content[s:e] if e != -1 else content[s:]

    @staticmethod
    def apply_filters(content: str, job: WatchJob) -> str:
        """Apply all configured filters."""
        if job.strip_html:
            content = ContentFilter.strip_html(content)
        if job.filter_regex:
            content = ContentFilter.grep(content, job.filter_regex)
        return content.strip()


# ── Diff Engine ────────────────────────────────────────────────────────────

class DiffEngine:
    """Compute diffs between content versions."""

    @staticmethod
    def compute(old: str, new: str) -> Tuple[List[str], Dict[str, int]]:
        """Compute unified diff and statistics."""
        old_lines = old.splitlines(keepends=True)
        new_lines = new.splitlines(keepends=True)
        diff = list(difflib.unified_diff(old_lines, new_lines,
                                          fromfile="previous", tofile="current",
                                          lineterm=""))
        stats = {
            "additions": sum(1 for l in diff if l.startswith("+") and not l.startswith("+++")),
            "deletions": sum(1 for l in diff if l.startswith("-") and not l.startswith("---")),
            "total_lines": len(diff),
        }
        return diff[:200], stats  # cap at 200 lines


# ── Watch History (SQLite) ─────────────────────────────────────────────────

class WatchHistory:
    """Persistent watch history for change tracking."""

    def __init__(self, db_path: str = ""):
        if not db_path:
            try:
                db_path = os.path.join(os.path.dirname(__file__), "..", ".urlwatch.db")
            except NameError:
                db_path = os.path.join(os.getcwd(), ".urlwatch.db")
        self.db_path = db_path
        self._init()

    def _init(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                url TEXT, content_hash TEXT,
                content TEXT, status_code INTEGER,
                fetched_at REAL,
                PRIMARY KEY (url, fetched_at)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                url TEXT PRIMARY KEY, name TEXT,
                interval_seconds INTEGER, strip_html INTEGER,
                filter_regex TEXT, enabled INTEGER
            )
        """)
        conn.commit()
        conn.close()

    def get_last(self, url: str) -> Optional[Tuple[str, str]]:
        """Get the last stored hash and content for a URL."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT content_hash, content FROM history WHERE url=? ORDER BY fetched_at DESC LIMIT 1", (url,))
        row = c.fetchone()
        conn.close()
        return (row[0], row[1]) if row else None

    def store(self, url: str, content_hash: str, content: str,
              status_code: int):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO history (url, content_hash, content, status_code, fetched_at) VALUES (?,?,?,?,?)",
            (url, content_hash, content[:50000], status_code, time.time()),
        )
        conn.commit()
        conn.close()

    def get_change_count(self, url: str) -> int:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(DISTINCT content_hash) FROM history WHERE url=?", (url,))
        count = c.fetchone()[0]
        conn.close()
        return count


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniUrlwatchEngine:
    """
    OMNI URLWatch Engine — Zero-Prod URL Change Monitoring.

    Capabilities (all native stdlib):
      - HTTP content fetching with custom headers
      - HTML stripping and regex content filtering
      - SHA256 content hashing for fast change detection
      - Unified diff generation with add/delete stats
      - SQLite history for persistent tracking
      - Batch URL monitoring
    """

    def __init__(self):
        self.fetcher = ContentFetcher()
        self.filters = ContentFilter()
        self.differ = DiffEngine()
        self.history = WatchHistory()

    def check(self, job: WatchJob) -> WatchResult:
        """Check a URL for changes."""
        result = WatchResult(url=job.url, name=job.name, fetched_at=time.time())

        # Fetch
        status, content, error = self.fetcher.fetch(job.url, job.headers)
        result.status_code = status
        if error:
            result.error = error
            result.change_type = ChangeType.ERROR
            return result

        # Filter
        filtered = self.filters.apply_filters(content, job)
        content_hash = hashlib.sha256(filtered.encode()).hexdigest()
        result.content_hash = content_hash
        result.content_length = len(filtered)

        # Compare with history
        last = self.history.get_last(job.url)
        if last is None:
            result.change_type = ChangeType.NEW
        elif last[0] == content_hash:
            result.change_type = ChangeType.UNCHANGED
        else:
            result.change_type = ChangeType.CHANGED
            diff_lines, stats = self.differ.compute(last[1], filtered)
            result.diff_lines = diff_lines
            result.diff_stats = stats

        # Store
        self.history.store(job.url, content_hash, filtered, status)
        return result

    def batch_check(self, jobs: List[WatchJob]) -> List[Dict]:
        """Check multiple URLs."""
        results = []
        for job in jobs:
            if not job.enabled:
                continue
            r = self.check(job)
            results.append({
                "url": r.url, "name": r.name,
                "status": r.status_code, "change": r.change_type.value,
                "hash": r.content_hash[:12], "size": r.content_length,
                "diff_stats": r.diff_stats, "error": r.error,
            })
        return results

    def diagnostics(self) -> Dict:
        return {
            "engine": "OmniUrlwatchEngine",
            "status": "active",
            "capabilities": ["http_fetch", "html_strip", "regex_filter",
                             "sha256_hash", "unified_diff", "sqlite_history",
                             "batch_monitor"],
        }


if __name__ == "__main__":
    engine = OmniUrlwatchEngine()
    job = WatchJob(url="https://httpbin.org/uuid", name="UUID Generator", strip_html=False)
    result = engine.check(job)
    print(json.dumps({
        "url": result.url, "status": result.status_code,
        "change": result.change_type.value, "hash": result.content_hash[:16],
    }, indent=2))
