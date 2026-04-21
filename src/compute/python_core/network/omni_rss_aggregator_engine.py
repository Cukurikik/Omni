ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI RSS AGGREGATOR ENGINE — RSS/Atom Feed Aggregation & News Digest
# ===========================================================================
# Source Paradigm: https://github.com/umputun/ralphex
# Domain Layer  : Network (RSS/News Aggregation)
# Zero-Mock     : 100% Native — urllib, re, json, xml.etree, sqlite3
# ===========================================================================
"""
Ralphex teaches us:
  1. RSS/Atom feed parsing and normalization
  2. Multi-feed aggregation with deduplication
  3. Content summarization and digest generation
  4. Feed health monitoring (stale, broken feeds)
  5. Keyword filtering and categorization
  6. Periodic feed checking with change detection

This engine distills those paradigms into OMNI-native Python for
RSS/Atom feed parsing, aggregation, and digest generation.
"""

import hashlib
import json
import os
import re
import sqlite3
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ── Data Models ──────────────────────────────────────────────────────────────

@dataclass
class FeedItem:
    title: str
    link: str
    description: str = ""
    pub_date: str = ""
    author: str = ""
    categories: List[str] = field(default_factory=list)
    content_hash: str = ""


@dataclass
class Feed:
    url: str
    title: str = ""
    items: List[FeedItem] = field(default_factory=list)
    last_fetched: float = 0
    error: str = ""
    item_count: int = 0


# ── RSS/Atom Parser ──────────────────────────────────────────────────────

class FeedParser:
    """Parse RSS 2.0 and Atom feeds."""

    @staticmethod
    def fetch_and_parse(url: str, timeout: int = 15) -> Feed:
        feed = Feed(url=url)
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "OMNI-RSSAggregator/1.0",
                "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml",
            })
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                xml_data = resp.read().decode("utf-8", errors="replace")
            feed.last_fetched = time.time()
            root = ET.fromstring(xml_data)

            # Detect Atom vs RSS
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            if root.tag == "{http://www.w3.org/2005/Atom}feed" or root.tag == "feed":
                return FeedParser._parse_atom(feed, root, ns)
            else:
                return FeedParser._parse_rss(feed, root)

        except ET.ParseError as e:
            feed.error = f"XML parse error: {str(e)[:100]}"
        except Exception as e:
            feed.error = str(e)[:200]
        return feed

    @staticmethod
    def _parse_rss(feed: Feed, root: ET.Element) -> Feed:
        channel = root.find("channel")
        if channel is None:
            channel = root
        feed.title = (channel.findtext("title") or "").strip()

        for item in channel.findall("item")[:50]:
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            desc = (item.findtext("description") or "").strip()
            desc = re.sub(r'<[^>]+>', '', desc)[:500]
            pub = (item.findtext("pubDate") or "").strip()
            author = (item.findtext("author") or item.findtext("{http://purl.org/dc/elements/1.1/}creator") or "").strip()
            cats = [c.text.strip() for c in item.findall("category") if c.text]
            ch = hashlib.sha256(f"{title}{link}".encode()).hexdigest()[:12]
            feed.items.append(FeedItem(title=title, link=link, description=desc,
                                        pub_date=pub, author=author,
                                        categories=cats, content_hash=ch))
        feed.item_count = len(feed.items)
        return feed

    @staticmethod
    def _parse_atom(feed: Feed, root: ET.Element, ns: Dict) -> Feed:
        feed.title = (root.findtext("{http://www.w3.org/2005/Atom}title") or
                       root.findtext("title") or "").strip()

        entries = (root.findall("{http://www.w3.org/2005/Atom}entry") or
                   root.findall("entry"))
        for entry in entries[:50]:
            title = (entry.findtext("{http://www.w3.org/2005/Atom}title") or
                     entry.findtext("title") or "").strip()
            link_el = (entry.find("{http://www.w3.org/2005/Atom}link") or
                       entry.find("link"))
            link = link_el.get("href", "") if link_el is not None else ""
            summary = (entry.findtext("{http://www.w3.org/2005/Atom}summary") or
                       entry.findtext("{http://www.w3.org/2005/Atom}content") or
                       entry.findtext("summary") or "").strip()
            summary = re.sub(r'<[^>]+>', '', summary)[:500]
            updated = (entry.findtext("{http://www.w3.org/2005/Atom}updated") or
                       entry.findtext("updated") or "").strip()
            author_el = (entry.find("{http://www.w3.org/2005/Atom}author") or
                         entry.find("author"))
            author = ""
            if author_el is not None:
                author = (author_el.findtext("{http://www.w3.org/2005/Atom}name") or
                          author_el.findtext("name") or "").strip()
            ch = hashlib.sha256(f"{title}{link}".encode()).hexdigest()[:12]
            feed.items.append(FeedItem(title=title, link=link, description=summary,
                                        pub_date=updated, author=author, content_hash=ch))
        feed.item_count = len(feed.items)
        return feed


# ── Feed Aggregator ──────────────────────────────────────────────────────

class FeedAggregator:
    """Aggregate multiple feeds with deduplication."""

    @staticmethod
    def aggregate(feeds: List[Feed]) -> List[FeedItem]:
        seen = set()
        all_items = []
        for feed in feeds:
            for item in feed.items:
                if item.content_hash not in seen:
                    seen.add(item.content_hash)
                    all_items.append(item)
        return all_items

    @staticmethod
    def filter_by_keywords(items: List[FeedItem], keywords: List[str]) -> List[FeedItem]:
        if not keywords:
            return items
        kw_lower = [k.lower() for k in keywords]
        return [i for i in items if any(
            k in i.title.lower() or k in i.description.lower() for k in kw_lower)]

    @staticmethod
    def generate_digest(items: List[FeedItem], max_items: int = 10) -> str:
        lines = [f"📰 OMNI News Digest ({len(items)} items)\n"]
        for i, item in enumerate(items[:max_items], 1):
            lines.append(f"{i}. **{item.title}**")
            if item.description:
                lines.append(f"   {item.description[:120]}...")
            lines.append(f"   🔗 {item.link}\n")
        return "\n".join(lines)


# ── Feed Store (SQLite) ──────────────────────────────────────────────────

class FeedStore:
    def __init__(self, db_path: str = ""):
        if not db_path:
            try:
                db_path = os.path.join(os.path.dirname(__file__), "..", ".rss_feeds.db")
            except NameError:
                db_path = os.path.join(os.getcwd(), ".rss_feeds.db")
        self.db_path = db_path
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                hash TEXT PRIMARY KEY, title TEXT,
                link TEXT, feed_url TEXT, fetched_at REAL
            )
        """)
        conn.commit()
        conn.close()

    def save_items(self, feed_url: str, items: List[FeedItem]):
        conn = sqlite3.connect(self.db_path)
        for item in items:
            conn.execute("INSERT OR IGNORE INTO items VALUES (?,?,?,?,?)",
                          (item.content_hash, item.title[:200], item.link[:500],
                           feed_url, time.time()))
        conn.commit()
        conn.close()

    def stats(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM items")
        total = c.fetchone()[0]
        c.execute("SELECT COUNT(DISTINCT feed_url) FROM items")
        feeds = c.fetchone()[0]
        conn.close()
        return {"total_items": total, "feeds_tracked": feeds}


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniRSSAggregatorEngine:
    """
    OMNI RSS Aggregator Engine — Zero-Mock Feed Aggregation & Digest.

    Capabilities (all native xml.etree + urllib):
      - RSS 2.0 and Atom feed parsing
      - Multi-feed aggregation with dedup
      - Keyword filtering
      - Digest generation (markdown)
      - Feed item persistence (SQLite)
    """

    def __init__(self):
        self.parser = FeedParser()
        self.aggregator = FeedAggregator()
        self.store = FeedStore()

    def fetch_feed(self, url: str) -> Dict:
        feed = self.parser.fetch_and_parse(url)
        if feed.items:
            self.store.save_items(url, feed.items)
        return {
            "url": url, "title": feed.title,
            "items": len(feed.items), "error": feed.error,
            "top": [{"title": i.title, "link": i.link[:80]} for i in feed.items[:5]],
        }

    def aggregate_feeds(self, urls: List[str]) -> Dict:
        feeds = [self.parser.fetch_and_parse(u) for u in urls]
        all_items = self.aggregator.aggregate(feeds)
        return {
            "feeds": len(urls), "total_items": len(all_items),
            "items": [{"title": i.title, "link": i.link[:80]} for i in all_items[:10]],
        }

    def diagnostics(self) -> Dict:
        return {
            "engine": "OmniRSSAggregatorEngine",
            "status": "active",
            "db": self.store.stats(),
            "capabilities": ["rss_parse", "atom_parse", "multi_aggregate",
                             "dedup", "keyword_filter", "digest_gen", "feed_store"],
        }


if __name__ == "__main__":
    engine = OmniRSSAggregatorEngine()
    print(json.dumps(engine.diagnostics(), indent=2))
