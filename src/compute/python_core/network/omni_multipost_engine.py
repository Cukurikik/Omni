ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI MULTIPOST ENGINE — Multi-Platform Content Publishing
# ===========================================================================
# Source Paradigm: https://github.com/leaperone/MultiPost-Extension
# Domain Layer  : Network (Content Distribution)
# Zero-Prod     : 100% Native — urllib, json, os, sqlite3, hashlib
# ===========================================================================
"""
MultiPost teaches us:
  1. One-click publishing to 10+ platforms simultaneously
  2. Content adaptation per platform (char limits, image ratios)
  3. Platform-specific formatting (markdown→html, hashtags, mentions)
  4. Publishing schedule management
  5. Post tracking and analytics
  6. API-based and browser-based publishing modes

This engine distills those paradigms into OMNI-native Python for
multi-platform content preparation, adaptation, and distribution.
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

class Platform(Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    MEDIUM = "medium"
    DEVTO = "dev.to"
    HASHNODE = "hashnode"
    REDDIT = "reddit"
    MASTODON = "mastodon"
    BLUESKY = "bluesky"
    CUSTOM_WEBHOOK = "webhook"


class PostStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"


@dataclass
class PlatformConfig:
    platform: Platform
    max_chars: int = 0          # 0 = unlimited
    supports_markdown: bool = False
    supports_images: bool = True
    max_images: int = 4
    hashtag_style: str = "#"    # "#" or none
    mention_style: str = "@"


@dataclass
class ContentPost:
    post_id: str
    title: str = ""
    body: str = ""
    tags: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    platforms: List[Platform] = field(default_factory=list)
    status: PostStatus = PostStatus.DRAFT
    scheduled_at: float = 0
    created_at: float = 0


# ── Platform Registry ─────────────────────────────────────────────────────

PLATFORM_CONFIGS: Dict[Platform, PlatformConfig] = {
    Platform.TWITTER: PlatformConfig(Platform.TWITTER, max_chars=280, supports_markdown=False, max_images=4),
    Platform.LINKEDIN: PlatformConfig(Platform.LINKEDIN, max_chars=3000, supports_markdown=False, max_images=9),
    Platform.FACEBOOK: PlatformConfig(Platform.FACEBOOK, max_chars=63206, supports_markdown=False),
    Platform.INSTAGRAM: PlatformConfig(Platform.INSTAGRAM, max_chars=2200, supports_markdown=False, max_images=10),
    Platform.MEDIUM: PlatformConfig(Platform.MEDIUM, max_chars=0, supports_markdown=True),
    Platform.DEVTO: PlatformConfig(Platform.DEVTO, max_chars=0, supports_markdown=True),
    Platform.HASHNODE: PlatformConfig(Platform.HASHNODE, max_chars=0, supports_markdown=True),
    Platform.REDDIT: PlatformConfig(Platform.REDDIT, max_chars=40000, supports_markdown=True),
    Platform.MASTODON: PlatformConfig(Platform.MASTODON, max_chars=500, supports_markdown=False),
    Platform.BLUESKY: PlatformConfig(Platform.BLUESKY, max_chars=300, supports_markdown=False),
}


# ── Content Adapter ────────────────────────────────────────────────────────

class ContentAdapter:
    """Adapt content for different platform requirements."""

    @staticmethod
    def adapt(body: str, tags: List[str], config: PlatformConfig) -> str:
        """Adapt content for a specific platform."""
        result = body

        # Strip markdown for non-markdown platforms
        if not config.supports_markdown:
            result = ContentAdapter._strip_markdown(result)

        # Add hashtags
        if tags and config.hashtag_style:
            hashtags = " ".join(f"{config.hashtag_style}{t.replace(' ', '')}" for t in tags[:10])
            result = f"{result}\n\n{hashtags}"

        # Truncate if needed
        if config.max_chars > 0 and len(result) > config.max_chars:
            result = result[:config.max_chars - 3] + "..."

        return result.strip()

    @staticmethod
    def _strip_markdown(text: str) -> str:
        """Remove markdown formatting."""
        text = re.sub(r'#{1,6}\s*', '', text)           # headers
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)    # bold
        text = re.sub(r'\*(.+?)\*', r'\1', text)        # italic
        text = re.sub(r'`(.+?)`', r'\1', text)          # inline code
        text = re.sub(r'```[\s\S]*?```', '', text)      # code blocks
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text) # links
        text = re.sub(r'!\[.*?\]\(.+?\)', '', text)     # images
        text = re.sub(r'^\s*[-*+]\s+', '• ', text, flags=re.MULTILINE)  # lists
        return text.strip()

    @staticmethod
    def preview_all(body: str, tags: List[str]) -> Dict[str, Dict]:
        """Preview adapted content for all platforms."""
        previews = {}
        for platform, config in PLATFORM_CONFIGS.items():
            adapted = ContentAdapter.adapt(body, tags, config)
            previews[platform.value] = {
                "chars": len(adapted),
                "max_chars": config.max_chars,
                "truncated": config.max_chars > 0 and len(adapted) >= config.max_chars,
                "preview": adapted[:200] + ("..." if len(adapted) > 200 else ""),
            }
        return previews


# ── Content Analyzer ───────────────────────────────────────────────────────

class ContentAnalyzer:
    """Analyze content quality and publishability."""

    @staticmethod
    def analyze(title: str, body: str, tags: List[str]) -> Dict:
        word_count = len(body.split())
        char_count = len(body)
        sentences = len(re.findall(r'[.!?]+', body))
        links = re.findall(r'https?://[^\s]+', body)
        mentions = re.findall(r'@\w+', body)
        hashtags_in = re.findall(r'#\w+', body)

        # Readability estimate
        avg_words_per_sentence = word_count / max(sentences, 1)
        reading_time_min = max(1, round(word_count / 200))

        return {
            "word_count": word_count,
            "char_count": char_count,
            "sentences": sentences,
            "links": len(links),
            "mentions": len(mentions),
            "hashtags": len(hashtags_in),
            "tags_provided": len(tags),
            "reading_time_min": reading_time_min,
            "avg_words_per_sentence": round(avg_words_per_sentence, 1),
            "has_title": bool(title),
            "platform_fit": {
                p.value: char_count <= (c.max_chars or float("inf"))
                for p, c in PLATFORM_CONFIGS.items()
            },
        }


# ── Post Store (SQLite) ──────────────────────────────────────────────────

class PostStore:
    def __init__(self, db_path: str = ""):
        if not db_path:
            try:
                db_path = os.path.join(os.path.dirname(__file__), "..", ".multipost.db")
            except NameError:
                db_path = os.path.join(os.getcwd(), ".multipost.db")
        self.db_path = db_path
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                post_id TEXT PRIMARY KEY, title TEXT,
                body TEXT, tags TEXT, platforms TEXT,
                status TEXT, created_at REAL
            )
        """)
        conn.commit()
        conn.close()

    def save(self, post: ContentPost):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT OR REPLACE INTO posts VALUES (?,?,?,?,?,?,?)",
            (post.post_id, post.title, post.body[:10000],
             json.dumps(post.tags), json.dumps([p.value for p in post.platforms]),
             post.status.value, post.created_at),
        )
        conn.commit()
        conn.close()

    def stats(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT status, COUNT(*) FROM posts GROUP BY status")
        by_status = {r[0]: r[1] for r in c.fetchall()}
        c.execute("SELECT COUNT(*) FROM posts")
        total = c.fetchone()[0]
        conn.close()
        return {"total": total, "by_status": by_status}


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniMultipostEngine:
    """
    OMNI MultiPost Engine — Zero-Prod Multi-Platform Content Publishing.

    Capabilities (all native stdlib):
      - Content adaptation per platform (10+ platforms)
      - Markdown stripping for social media
      - Character limit enforcement with smart truncation
      - Content quality analysis (readability, fit)
      - Multi-platform preview generation
      - SQLite post persistence
    """

    def __init__(self):
        self.adapter = ContentAdapter()
        self.analyzer = ContentAnalyzer()
        self.store = PostStore()

    def create_post(self, title: str, body: str, tags: List[str] = None,
                     platforms: List[str] = None) -> Dict:
        post_id = hashlib.sha256(f"{title}{time.time()}".encode()).hexdigest()[:12]
        plats = []
        for p in (platforms or ["twitter", "linkedin"]):
            try:
                plats.append(Platform(p))
            except ValueError:
                pass

        post = ContentPost(
            post_id=post_id, title=title, body=body,
            tags=tags or [], platforms=plats, created_at=time.time(),
        )
        self.store.save(post)
        analysis = self.analyzer.analyze(title, body, tags or [])
        previews = self.adapter.preview_all(body, tags or [])
        return {
            "post_id": post_id, "title": title,
            "analysis": analysis,
            "previews": {p: previews[p] for p in [pl.value for pl in plats] if p in previews},
        }

    def diagnostics(self) -> Dict:
        return {
            "engine": "OmniMultipostEngine",
            "status": "active",
            "platforms": [p.value for p in Platform],
            "db": self.store.stats(),
            "capabilities": ["content_adapt", "markdown_strip", "char_limit",
                             "quality_analysis", "multi_preview", "post_store"],
        }


if __name__ == "__main__":
    engine = OmniMultipostEngine()
    r = engine.create_post(
        "OMNI Framework Launch",
        "We're launching **OMNI Framework** — the world's first polylingual runtime. "
        "Built with #Rust, #Go, and #Python for maximum performance.",
        tags=["omni", "devtools", "launch"],
        platforms=["twitter", "linkedin", "medium"],
    )
    print(json.dumps(r, indent=2))
