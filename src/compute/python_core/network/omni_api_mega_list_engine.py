ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI API MEGA LIST ENGINE — Universal Public API Catalog & Probe
# ===========================================================================
# Source Paradigm: https://github.com/cporter202/API-mega-list
# Domain Layer  : Network (API Directory)
# Zero-Prod     : 100% Native — urllib, json, sqlite3, real HTTP probing
# ===========================================================================
"""
API-mega-list teaches us:
  1. Curated catalog of thousands of production-ready public APIs
  2. Category taxonomy: AI, Automation, Business, DevTools, Social, etc.
  3. API health checking and availability monitoring
  4. Structured metadata: name, URL, description, auth requirement, pricing
  5. Quick discovery for building integrations without reinventing the wheel

This engine distills those paradigms into OMNI-native Python for
maintaining a queryable API catalog with live health probing.
"""

import json
import os
import socket
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ── Data Models ──────────────────────────────────────────────────────────────

@dataclass
class APIEntry:
    name: str
    url: str
    description: str
    category: str
    auth: str = "none"            # "none" | "apiKey" | "oauth" | "token"
    pricing: str = "free"         # "free" | "freemium" | "paid"
    cors: str = "unknown"         # "yes" | "no" | "unknown"
    https: bool = True
    is_healthy: bool = True
    last_checked: float = 0
    response_time_ms: float = 0


# ── Built-In API Catalog ────────────────────────────────────────────────────

BUILTIN_APIS: List[Dict] = [
    # AI & Machine Learning
    {"name": "OpenAI", "url": "https://api.openai.com/v1/models", "description": "GPT models, DALL-E, Whisper", "category": "ai", "auth": "token", "pricing": "paid"},
    {"name": "Gemini", "url": "https://generativelanguage.googleapis.com", "description": "Google Gemini/PaLM language models", "category": "ai", "auth": "apiKey", "pricing": "freemium"},
    {"name": "HuggingFace", "url": "https://huggingface.co/api/models", "description": "Open-source AI model hub", "category": "ai", "auth": "none", "pricing": "free"},
    {"name": "Replicate", "url": "https://api.replicate.com/v1/models", "description": "Run ML models via API", "category": "ai", "auth": "token", "pricing": "paid"},
    {"name": "Stability AI", "url": "https://api.stability.ai/v1/engines/list", "description": "Stable Diffusion image generation", "category": "ai", "auth": "apiKey", "pricing": "freemium"},

    # Developer Tools
    {"name": "GitHub API", "url": "https://api.github.com", "description": "GitHub repositories, issues, PRs", "category": "devtools", "auth": "token", "pricing": "free"},
    {"name": "GitLab API", "url": "https://gitlab.com/api/v4/projects", "description": "GitLab project management", "category": "devtools", "auth": "token", "pricing": "free"},
    {"name": "NPM Registry", "url": "https://registry.npmjs.org", "description": "NPM package metadata", "category": "devtools", "auth": "none", "pricing": "free"},
    {"name": "PyPI", "url": "https://pypi.org/pypi/requests/json", "description": "Python package index", "category": "devtools", "auth": "none", "pricing": "free"},
    {"name": "crates.io", "url": "https://crates.io/api/v1/crates?page=1&per_page=1", "description": "Rust package registry", "category": "devtools", "auth": "none", "pricing": "free"},

    # Data & Analytics
    {"name": "REST Countries", "url": "https://restcountries.com/v3.1/all", "description": "Country data (name, capital, currency)", "category": "data", "auth": "none", "pricing": "free"},
    {"name": "Open Meteo", "url": "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current_weather=true", "description": "Free weather data", "category": "data", "auth": "none", "pricing": "free"},
    {"name": "JSONPlaceholder", "url": "https://jsonplaceholder.typicode.com/posts/1", "description": "Fake REST API for testing", "category": "data", "auth": "none", "pricing": "free"},
    {"name": "CoinGecko", "url": "https://api.coingecko.com/api/v3/ping", "description": "Cryptocurrency price data", "category": "finance", "auth": "none", "pricing": "freemium"},

    # Social & Communication
    {"name": "Discord API", "url": "https://discord.com/api/v10/gateway", "description": "Discord bots and messaging", "category": "social", "auth": "token", "pricing": "free"},
    {"name": "Telegram Bot API", "url": "https://api.telegram.org", "description": "Telegram bot management", "category": "social", "auth": "token", "pricing": "free"},
    {"name": "Reddit API", "url": "https://www.reddit.com/r/programming.json?limit=1", "description": "Reddit posts and comments", "category": "social", "auth": "none", "pricing": "free"},

    # Business & Payments
    {"name": "Stripe API", "url": "https://api.stripe.com/v1/charges", "description": "Payment processing", "category": "business", "auth": "token", "pricing": "paid"},
    {"name": "Exchange Rates", "url": "https://open.er-api.com/v6/latest/USD", "description": "Currency exchange rates", "category": "finance", "auth": "none", "pricing": "free"},

    # Media & Entertainment
    {"name": "TMDB", "url": "https://api.themoviedb.org/3/movie/popular", "description": "Movie and TV show database", "category": "media", "auth": "apiKey", "pricing": "free"},
    {"name": "Spotify API", "url": "https://api.spotify.com/v1/browse/categories", "description": "Music catalog and playback", "category": "media", "auth": "oauth", "pricing": "freemium"},

    # Cloud & Infrastructure
    {"name": "IP API", "url": "https://ipapi.co/json/", "description": "IP geolocation lookup", "category": "infrastructure", "auth": "none", "pricing": "freemium"},
    {"name": "DNS Over HTTPS", "url": "https://dns.google/resolve?name=google.com&type=A", "description": "DNS resolution via HTTPS", "category": "infrastructure", "auth": "none", "pricing": "free"},

    # Security
    {"name": "Have I Been Pwned", "url": "https://haveibeenpwned.com/api/v3/breaches", "description": "Data breach lookup", "category": "security", "auth": "apiKey", "pricing": "freemium"},
    {"name": "VirusTotal", "url": "https://www.virustotal.com/api/v3/files", "description": "File/URL malware scanning", "category": "security", "auth": "apiKey", "pricing": "freemium"},

    # Automation & Agents
    {"name": "Zapier NLA", "url": "https://nla.zapier.com/api/v1/exposed/", "description": "Natural language action automation", "category": "automation", "auth": "token", "pricing": "freemium"},
]


# ── API Health Prober ───────────────────────────────────────────────────────

class APIProber:
    """Probe API endpoints for availability and latency."""

    @staticmethod
    def probe(url: str, timeout: float = 8.0) -> Dict:
        """Check if an API endpoint is reachable and measure response time."""
        start = time.perf_counter()
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "OMNI-APIProbe/1.0", "Accept": "application/json"},
            )
            import ssl
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
                latency = (time.perf_counter() - start) * 1000
                return {
                    "url": url,
                    "status": resp.getcode(),
                    "healthy": True,
                    "latency_ms": round(latency, 2),
                    "content_type": resp.headers.get("Content-Type", ""),
                }
        except urllib.error.HTTPError as e:
            latency = (time.perf_counter() - start) * 1000
            return {
                "url": url, "status": e.code, "healthy": e.code < 500,
                "latency_ms": round(latency, 2), "error": str(e.reason)[:100],
            }
        except Exception as e:
            latency = (time.perf_counter() - start) * 1000
            return {
                "url": url, "status": 0, "healthy": False,
                "latency_ms": round(latency, 2), "error": str(e)[:128],
            }


# ── Catalog Database (SQLite) ──────────────────────────────────────────────

class APICatalogDB:
    """Persistent API catalog with health check history."""

    def __init__(self, db_path: str = ""):
        if not db_path:
            db_path = os.path.join(os.path.dirname(__file__), "..", ".api_catalog.db")
        self.db_path = db_path
        self._init()

    def _init(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS apis (
                name TEXT PRIMARY KEY,
                url TEXT, description TEXT, category TEXT,
                auth TEXT, pricing TEXT, https INTEGER,
                is_healthy INTEGER DEFAULT 1,
                last_checked REAL DEFAULT 0,
                response_time_ms REAL DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()

    def upsert(self, api: APIEntry):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """INSERT OR REPLACE INTO apis
            (name,url,description,category,auth,pricing,https,is_healthy,last_checked,response_time_ms)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (api.name, api.url, api.description, api.category,
             api.auth, api.pricing, int(api.https),
             int(api.is_healthy), api.last_checked, api.response_time_ms),
        )
        conn.commit()
        conn.close()

    def search(self, query: str) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "SELECT name,url,description,category,auth,pricing,is_healthy FROM apis WHERE name LIKE ? OR description LIKE ? OR category LIKE ?",
            (f"%{query}%", f"%{query}%", f"%{query}%"),
        )
        cols = ["name", "url", "description", "category", "auth", "pricing", "is_healthy"]
        rows = [dict(zip(cols, row)) for row in c.fetchall()]
        conn.close()
        return rows

    def get_by_category(self, category: str) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT name,url,description,auth,pricing FROM apis WHERE category=?", (category,))
        cols = ["name", "url", "description", "auth", "pricing"]
        rows = [dict(zip(cols, row)) for row in c.fetchall()]
        conn.close()
        return rows

    def stats(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT category, COUNT(*) FROM apis GROUP BY category ORDER BY COUNT(*) DESC")
        cats = {row[0]: row[1] for row in c.fetchall()}
        c.execute("SELECT COUNT(*) FROM apis")
        total = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM apis WHERE is_healthy=1")
        healthy = c.fetchone()[0]
        conn.close()
        return {"total": total, "healthy": healthy, "categories": cats}


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniApiMegaListEngine:
    """
    OMNI API Mega List Engine — Zero-Prod Public API Catalog & Health Prober.

    Capabilities (all native stdlib):
      - 25+ built-in API entries across 10 categories
      - Live API endpoint health probing (urllib + SSL)
      - SQLite-backed persistent catalog
      - Search by name/description/category
      - Category-based browsing
      - Health statistics
    """

    def __init__(self):
        self.prober = APIProber()
        self.db = APICatalogDB()
        self._seed_catalog()

    def _seed_catalog(self):
        """Seed the database with built-in API entries."""
        for api_dict in BUILTIN_APIS:
            entry = APIEntry(
                name=api_dict["name"],
                url=api_dict["url"],
                description=api_dict["description"],
                category=api_dict["category"],
                auth=api_dict.get("auth", "none"),
                pricing=api_dict.get("pricing", "free"),
            )
            self.db.upsert(entry)

    def search(self, query: str) -> List[Dict]:
        """Search the API catalog."""
        return self.db.search(query)

    def browse_category(self, category: str) -> List[Dict]:
        """Browse APIs by category."""
        return self.db.get_by_category(category)

    def probe_api(self, name: str) -> Dict:
        """Probe a specific API from the catalog."""
        results = self.db.search(name)
        if not results:
            return {"error": f"API '{name}' not found"}
        url = results[0]["url"]
        probe = self.prober.probe(url)

        # Update health status in DB
        entry = APIEntry(
            name=results[0]["name"], url=url,
            description=results[0]["description"],
            category=results[0]["category"],
            auth=results[0]["auth"], pricing=results[0]["pricing"],
            is_healthy=probe.get("healthy", False),
            last_checked=time.time(),
            response_time_ms=probe.get("latency_ms", 0),
        )
        self.db.upsert(entry)

        return probe

    def health_check_all(self, max_apis: int = 10) -> Dict:
        """Probe the first N APIs and return health summary."""
        results = []
        for api_dict in BUILTIN_APIS[:max_apis]:
            probe = self.prober.probe(api_dict["url"])
            results.append({
                "name": api_dict["name"],
                "category": api_dict["category"],
                "healthy": probe.get("healthy", False),
                "latency_ms": probe.get("latency_ms", 0),
                "status": probe.get("status", 0),
            })
        healthy = sum(1 for r in results if r["healthy"])
        return {
            "checked": len(results),
            "healthy": healthy,
            "unhealthy": len(results) - healthy,
            "results": results,
        }

    def diagnostics(self) -> Dict:
        stats = self.db.stats()
        return {
            "engine": "OmniApiMegaListEngine",
            "status": "active",
            "catalog_size": stats["total"],
            "categories": stats["categories"],
            "capabilities": ["api_catalog", "live_probe", "category_browse",
                             "search", "health_monitor", "sqlite_persistence"],
        }


if __name__ == "__main__":
    engine = OmniApiMegaListEngine()
    print("[APIMegaList] Catalog Stats:")
    print(json.dumps(engine.diagnostics(), indent=2))
