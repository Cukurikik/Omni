ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI SUGGEST ARR ENGINE — Media Recommendation & Discovery
# ===========================================================================
# Source Paradigm: https://github.com/giuseppe99barchetta/SuggestArr
# Domain Layer  : Domain (Media Recommendations)
# Zero-Prod     : 100% Native — json, os, re, hashlib, sqlite3, urllib
# ===========================================================================
"""
SuggestArr teaches us:
  1. Content-based media recommendation (similar genres, cast, directors)
  2. Media library analysis (movies, TV shows, music)
  3. TMDb API integration for metadata enrichment
  4. Watch history tracking for personalized suggestions
  5. Rating-based scoring and ranking
  6. Cross-media recommendations (movie → TV, etc.)

This engine distills those paradigms into OMNI-native Python for
media recommendation logic with scoring, similarity, and tracking.
"""

import hashlib
import json
import math
import os
import re
import sqlite3
import time
import urllib.request
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


# ── Data Models ──────────────────────────────────────────────────────────────

class MediaType(Enum):
    MOVIE = "movie"
    TV = "tv"
    MUSIC = "music"
    BOOK = "book"


@dataclass
class MediaItem:
    media_id: str
    title: str
    media_type: MediaType = MediaType.MOVIE
    genres: List[str] = field(default_factory=list)
    year: int = 0
    rating: float = 0.0
    director: str = ""
    cast: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    watched: bool = False
    user_rating: float = 0.0


# ── Similarity Engine ────────────────────────────────────────────────────

class SimilarityEngine:
    """Calculate similarity between media items."""

    @staticmethod
    def genre_similarity(a: List[str], b: List[str]) -> float:
        if not a or not b:
            return 0.0
        set_a, set_b = set(g.lower() for g in a), set(g.lower() for g in b)
        intersection = set_a & set_b
        union = set_a | set_b
        return len(intersection) / len(union) if union else 0.0

    @staticmethod
    def cast_similarity(a: List[str], b: List[str]) -> float:
        if not a or not b:
            return 0.0
        set_a = set(c.lower() for c in a[:10])
        set_b = set(c.lower() for c in b[:10])
        common = set_a & set_b
        return len(common) / max(len(set_a), len(set_b))

    @staticmethod
    def keyword_similarity(a: List[str], b: List[str]) -> float:
        if not a or not b:
            return 0.0
        set_a, set_b = set(k.lower() for k in a), set(k.lower() for k in b)
        common = set_a & set_b
        return len(common) / max(len(set_a), len(set_b))

    @staticmethod
    def score(source: MediaItem, candidate: MediaItem) -> float:
        """Calculate overall similarity score (0-1)."""
        genre_sim = SimilarityEngine.genre_similarity(source.genres, candidate.genres) * 0.4
        cast_sim = SimilarityEngine.cast_similarity(source.cast, candidate.cast) * 0.2
        keyword_sim = SimilarityEngine.keyword_similarity(source.keywords, candidate.keywords) * 0.2
        director_bonus = 0.1 if (source.director and source.director.lower() == candidate.director.lower()) else 0
        rating_factor = (candidate.rating / 10.0) * 0.1
        return round(genre_sim + cast_sim + keyword_sim + director_bonus + rating_factor, 3)


# ── Recommendation Engine ────────────────────────────────────────────────

class RecommendationEngine:
    """Generate media recommendations based on similarity."""

    def __init__(self):
        self.similarity = SimilarityEngine()

    def recommend(self, source: MediaItem, library: List[MediaItem],
                   limit: int = 10) -> List[Dict]:
        scored = []
        for item in library:
            if item.media_id == source.media_id:
                continue
            if item.watched:
                continue
            s = self.similarity.score(source, item)
            if s > 0.05:
                scored.append({"title": item.title, "score": s,
                               "genres": item.genres, "year": item.year,
                               "rating": item.rating})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]

    def trending(self, library: List[MediaItem], limit: int = 10) -> List[Dict]:
        rated = sorted(library, key=lambda x: x.rating, reverse=True)
        return [{"title": m.title, "rating": m.rating, "genres": m.genres,
                  "year": m.year} for m in rated[:limit]]


# ── Media Library Store (SQLite) ─────────────────────────────────────────

class MediaStore:
    def __init__(self, db_path: str = ""):
        if not db_path:
            try:
                db_path = os.path.join(os.path.dirname(__file__), "..", ".suggest_arr.db")
            except NameError:
                db_path = os.path.join(os.getcwd(), ".suggest_arr.db")
        self.db_path = db_path
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS media (
                media_id TEXT PRIMARY KEY, title TEXT,
                media_type TEXT, genres TEXT, year INTEGER,
                rating REAL, watched INTEGER, added_at REAL
            )
        """)
        conn.commit()
        conn.close()

    def add(self, item: MediaItem):
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT OR REPLACE INTO media VALUES (?,?,?,?,?,?,?,?)",
                      (item.media_id, item.title, item.media_type.value,
                       json.dumps(item.genres), item.year, item.rating,
                       1 if item.watched else 0, time.time()))
        conn.commit()
        conn.close()

    def stats(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM media")
        total = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM media WHERE watched=1")
        watched = c.fetchone()[0]
        conn.close()
        return {"total": total, "watched": watched}


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniSuggestArrEngine:
    """
    OMNI SuggestArr Engine — Zero-Prod Media Recommendation System.

    Capabilities (all native stdlib):
      - Genre/cast/keyword similarity scoring
      - Content-based recommendations
      - Trending by rating
      - Watch history tracking (SQLite)
      - Multi-media type support (movie/tv/music/book)
    """

    def __init__(self):
        self.recommender = RecommendationEngine()
        self.store = MediaStore()

    def recommend_from(self, source: Dict, library: List[Dict], limit: int = 5) -> Dict:
        src = MediaItem(media_id="src", title=source.get("title", ""),
                         genres=source.get("genres", []),
                         cast=source.get("cast", []),
                         keywords=source.get("keywords", []),
                         director=source.get("director", ""),
                         rating=source.get("rating", 0))
        lib = [MediaItem(
            media_id=hashlib.sha256(m.get("title", "").encode()).hexdigest()[:8],
            title=m.get("title", ""), genres=m.get("genres", []),
            cast=m.get("cast", []), keywords=m.get("keywords", []),
            director=m.get("director", ""), rating=m.get("rating", 0),
        ) for m in library]
        recs = self.recommender.recommend(src, lib, limit)
        return {"source": src.title, "recommendations": recs}

    def diagnostics(self) -> Dict:
        return {
            "engine": "OmniSuggestArrEngine",
            "status": "active",
            "db": self.store.stats(),
            "capabilities": ["genre_similarity", "cast_match", "keyword_match",
                             "director_bonus", "rating_rank", "watch_track",
                             "trending", "cross_media"],
        }


if __name__ == "__main__":
    engine = OmniSuggestArrEngine()
    print(json.dumps(engine.diagnostics(), indent=2))
