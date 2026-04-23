ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI PAGE AGENT ENGINE — DOM Semantic Analysis & Web Accessibility
# ===========================================================================
# Source Paradigm: https://github.com/anthropics/anthropic-cookbook (page-agent)
# Domain Layer  : Network (DOM Analysis)
# Zero-Prod     : 100% Native — urllib, re, html.parser, json, sqlite3
# ===========================================================================
"""
Page Agent teaches us:
  1. Full DOM tree extraction from web pages
  2. Semantic element analysis (headings, links, forms, tables, lists)
  3. Accessibility audit (alt text, ARIA roles, heading hierarchy)
  4. CSS selector-based element targeting
  5. Page structure scoring and quality metrics
  6. Meta tag and SEO extraction

This engine distills those paradigms into OMNI-native Python for
comprehensive DOM analysis using html.parser and urllib.
"""

import hashlib
import json
import os
import re
import sqlite3
import time
import urllib.request
import urllib.error
from html.parser import HTMLParser
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ── DOM Parser ────────────────────────────────────────────────────────────

class DOMAnalyzer(HTMLParser):
    """Full HTML DOM semantic analyzer using stdlib html.parser."""

    def __init__(self):
        super().__init__()
        self.headings: List[Dict] = []          # h1-h6
        self.links: List[Dict] = []             # a tags
        self.images: List[Dict] = []            # img tags
        self.forms: List[Dict] = []             # form tags
        self.inputs: List[Dict] = []            # input tags
        self.buttons: List[Dict] = []           # button tags
        self.tables: int = 0
        self.lists: int = 0                     # ul, ol
        self.scripts: int = 0
        self.styles: int = 0
        self.meta_tags: List[Dict] = []
        self.title: str = ""
        self.aria_elements: int = 0
        self.total_elements: int = 0
        self._tag_stack: List[str] = []
        self._current_text: str = ""
        self._in_title: bool = False
        self._imgs_without_alt: int = 0
        self._heading_order: List[int] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        self.total_elements += 1
        attr_dict = {k: v or "" for k, v in attrs}
        self._tag_stack.append(tag)

        # Check ARIA attributes
        if any(k.startswith("aria-") or k == "role" for k, _ in attrs):
            self.aria_elements += 1

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag[1])
            self._heading_order.append(level)
            self._current_text = ""

        elif tag == "a":
            self.links.append({
                "href": attr_dict.get("href", "")[:200],
                "text": "",
                "rel": attr_dict.get("rel", ""),
            })
            self._current_text = ""

        elif tag == "img":
            alt = attr_dict.get("alt", "")
            src = attr_dict.get("src", "")[:200]
            self.images.append({"src": src, "alt": alt, "has_alt": bool(alt)})
            if not alt:
                self._imgs_without_alt += 1

        elif tag == "form":
            self.forms.append({
                "action": attr_dict.get("action", "")[:200],
                "method": attr_dict.get("method", "get").upper(),
                "id": attr_dict.get("id", ""),
            })

        elif tag == "input":
            self.inputs.append({
                "type": attr_dict.get("type", "text"),
                "name": attr_dict.get("name", ""),
                "id": attr_dict.get("id", ""),
                "required": "required" in attr_dict,
                "has_label": bool(attr_dict.get("aria-label", "") or
                                   attr_dict.get("placeholder", "")),
            })

        elif tag == "button":
            self.buttons.append({
                "type": attr_dict.get("type", "button"),
                "id": attr_dict.get("id", ""),
                "text": "",
            })
            self._current_text = ""

        elif tag == "table":
            self.tables += 1
        elif tag in ("ul", "ol"):
            self.lists += 1
        elif tag == "script":
            self.scripts += 1
        elif tag in ("style", "link") and attr_dict.get("rel") == "stylesheet":
            self.styles += 1
        elif tag == "meta":
            self.meta_tags.append(attr_dict)
        elif tag == "title":
            self._in_title = True
            self._current_text = ""

    def handle_endtag(self, tag: str):
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag[1])
            self.headings.append({"level": level, "text": self._current_text.strip()[:100]})

        elif tag == "a" and self.links:
            self.links[-1]["text"] = self._current_text.strip()[:80]

        elif tag == "button" and self.buttons:
            self.buttons[-1]["text"] = self._current_text.strip()[:50]

        elif tag == "title":
            self.title = self._current_text.strip()
            self._in_title = False

        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

    def handle_data(self, data: str):
        self._current_text += data

    def get_report(self) -> Dict:
        # SEO extraction from meta tags
        description = ""
        og_image = ""
        canonical = ""
        for m in self.meta_tags:
            if m.get("name", "").lower() == "description":
                description = m.get("content", "")[:300]
            if m.get("property", "").lower() == "og:image":
                og_image = m.get("content", "")[:200]

        # Accessibility score (0-100)
        a11y_score = 100
        if self._imgs_without_alt:
            a11y_score -= min(30, self._imgs_without_alt * 5)
        inputs_without_labels = sum(1 for i in self.inputs if not i.get("has_label"))
        if inputs_without_labels:
            a11y_score -= min(20, inputs_without_labels * 5)
        h1_count = sum(1 for h in self.headings if h["level"] == 1)
        if h1_count == 0:
            a11y_score -= 10
        elif h1_count > 1:
            a11y_score -= 5
        # Heading hierarchy check
        if self._heading_order:
            for i in range(1, len(self._heading_order)):
                if self._heading_order[i] - self._heading_order[i-1] > 1:
                    a11y_score -= 5
                    break
        a11y_score = max(0, a11y_score)

        return {
            "title": self.title,
            "seo": {"description": description, "og_image": og_image},
            "structure": {
                "total_elements": self.total_elements,
                "headings": len(self.headings),
                "links": len(self.links),
                "images": len(self.images),
                "forms": len(self.forms),
                "inputs": len(self.inputs),
                "buttons": len(self.buttons),
                "tables": self.tables,
                "lists": self.lists,
                "scripts": self.scripts,
            },
            "headings": self.headings[:10],
            "accessibility": {
                "score": a11y_score,
                "aria_elements": self.aria_elements,
                "images_without_alt": self._imgs_without_alt,
                "inputs_without_labels": inputs_without_labels,
                "h1_count": h1_count,
            },
        }


# ── Page Fetcher ──────────────────────────────────────────────────────────

class PageFetcher:
    @staticmethod
    def fetch(url: str, timeout: int = 15) -> Dict:
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (OMNI-PageAgent/1.0)",
                "Accept": "text/html,application/xhtml+xml",
            })
            start = time.perf_counter()
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                html = resp.read().decode("utf-8", errors="replace")
                return {
                    "url": url, "status": resp.getcode(),
                    "html": html, "size_kb": round(len(html) / 1024, 2),
                    "ms": round((time.perf_counter() - start) * 1000, 2),
                }
        except Exception as e:
            return {"url": url, "error": str(e)[:256]}


# ── Page Store (SQLite) ──────────────────────────────────────────────────

class PageStore:
    def __init__(self, db_path: str = ""):
        if not db_path:
            try:
                db_path = os.path.join(os.path.dirname(__file__), "..", ".page_agent.db")
            except NameError:
                db_path = os.path.join(os.getcwd(), ".page_agent.db")
        self.db_path = db_path
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pages (
                url_hash TEXT PRIMARY KEY, url TEXT,
                title TEXT, elements INTEGER,
                a11y_score INTEGER, crawled_at REAL
            )
        """)
        conn.commit()
        conn.close()

    def save(self, url: str, report: Dict):
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:12]
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT OR REPLACE INTO pages VALUES (?,?,?,?,?,?)",
                      (url_hash, url[:500], report.get("title", ""),
                       report.get("structure", {}).get("total_elements", 0),
                       report.get("accessibility", {}).get("score", 0), time.time()))
        conn.commit()
        conn.close()

    def stats(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM pages")
        total = c.fetchone()[0]
        conn.close()
        return {"pages_analyzed": total}


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniPageAgentEngine:
    """
    OMNI Page Agent Engine — Zero-Prod DOM Semantic Analysis.

    Capabilities (all native html.parser + urllib):
      - Full DOM tree parsing and element extraction
      - Semantic analysis (headings, links, forms, tables, buttons)
      - Accessibility audit with scoring (0-100)
      - SEO meta extraction (title, description, OG tags)
      - Image alt-text compliance checking
      - Input label coverage analysis
      - Page structure persistence (SQLite)
    """

    def __init__(self):
        self.fetcher = PageFetcher()
        self.store = PageStore()

    def analyze(self, url: str) -> Dict:
        page = self.fetcher.fetch(url)
        if "error" in page:
            return page
        analyzer = DOMAnalyzer()
        analyzer.feed(page["html"])
        report = analyzer.get_report()
        report["url"] = url
        report["fetch"] = {"status": page["status"],
                            "size_kb": page["size_kb"], "ms": page["ms"]}
        self.store.save(url, report)
        return report

    def diagnostics(self) -> Dict:
        return {
            "engine": "OmniPageAgentEngine",
            "status": "active",
            "db": self.store.stats(),
            "capabilities": ["dom_parse", "heading_extract", "link_extract",
                             "form_analyze", "image_audit", "a11y_score",
                             "seo_extract", "input_label_check", "page_persist"],
        }


if __name__ == "__main__":
    engine = OmniPageAgentEngine()
    print(json.dumps(engine.diagnostics(), indent=2))
