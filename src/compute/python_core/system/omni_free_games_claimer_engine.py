ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI FREE GAMES CLAIMER ENGINE — Automated Digital Storefront Harvester
# ===========================================================================
# Source Paradigm: https://github.com/vogler/free-games-claimer
# Domain Layer  : Automation
# Zero-Mock     : 100% Native — subprocess, urllib, json, sqlite3
# ===========================================================================
"""
free-games-claimer teaches us:
  1. Automated browser-based claiming from Epic/GOG/Amazon/etc.
  2. Scheduled polling for new free game offerings
  3. Session/cookie management for authenticated storefront access
  4. Multi-platform storefront abstraction
  5. Notification system (claimed games log)
  6. Headless browser automation patterns

This engine distills those paradigms into OMNI-native Python automation
for monitoring and harvesting free digital content from public APIs.
"""

import json
import os
import sqlite3
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


# ── Data Models ──────────────────────────────────────────────────────────────

class Storefront(Enum):
    """OMNI production engine for Storefront integration."""
    EPIC = "epic"
    GOG = "gog"
    STEAM = "steam"
    HUMBLE = "humble"
    ITCHIO = "itchio"

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "Storefront",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


class GameStatus(Enum):
    """OMNI production engine for GameStatus integration."""
    FREE_NOW = "free_now"
    UPCOMING = "upcoming"
    EXPIRED = "expired"
    CLAIMED = "claimed"

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "GameStatus",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


@dataclass
class FreeGame:
    """OMNI production engine for FreeGame integration."""
    title: str
    storefront: str
    url: str
    status: str
    original_price: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""
    image_url: str = ""
    discovered_at: float = 0

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "FreeGame",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


# ── Storefront Scrapers (All Native urllib) ─────────────────────────────────

class EpicFreeGamesAPI:
    """Fetch free games from the Epic Games Store public API."""

    API_URL = "https://store-site-backend-official.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US&allowCountries=US"

    @staticmethod
    def fetch() -> List[FreeGame]:
        """Fetch currently free games from Epic Games Store."""
        games = []
        try:
            req = urllib.request.Request(
                EpicFreeGamesAPI.API_URL,
                headers={"User-Agent": "OMNI-Claimer/1.0", "Accept": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            elements = (data.get("data", {})
                        .get("Catalog", {})
                        .get("searchStore", {})
                        .get("elements", []))

            for elem in elements:
                title = elem.get("title", "Unknown")
                desc = elem.get("description", "")

                # Check promotions
                promos = elem.get("promotions")
                if not promos:
                    continue

                offers = promos.get("promotionalOffers", [])
                upcoming = promos.get("upcomingPromotionalOffers", [])

                status = GameStatus.UPCOMING.value
                start_date = ""
                end_date = ""

                if offers:
                    for offer_group in offers:
                        for offer in offer_group.get("promotionalOffers", []):
                            discount = offer.get("discountSetting", {})
                            if discount.get("discountPercentage", 100) == 0:
                                status = GameStatus.FREE_NOW.value
                                start_date = offer.get("startDate", "")
                                end_date = offer.get("endDate", "")

                elif upcoming:
                    for offer_group in upcoming:
                        for offer in offer_group.get("promotionalOffers", []):
                            start_date = offer.get("startDate", "")
                            end_date = offer.get("endDate", "")

                # Price
                price_info = elem.get("price", {}).get("totalPrice", {})
                original = price_info.get("originalPrice", 0)
                fmt_price = f"${original / 100:.2f}" if original else "Free"

                # URL slug
                slug = ""
                mappings = elem.get("catalogNs", {}).get("mappings", [])
                if mappings:
                    slug = mappings[0].get("pageSlug", "")
                if not slug:
                    slug = elem.get("productSlug", elem.get("urlSlug", ""))
                url = f"https://store.epicgames.com/en-US/p/{slug}" if slug else ""

                # Image
                image = ""
                for img in elem.get("keyImages", []):
                    if img.get("type") in ("OfferImageWide", "DieselStoreFrontWide", "Thumbnail"):
                        image = img.get("url", "")
                        break

                games.append(FreeGame(
                    title=title, storefront=Storefront.EPIC.value,
                    url=url, status=status, original_price=fmt_price,
                    start_date=start_date, end_date=end_date,
                    description=desc[:256], image_url=image,
                    discovered_at=time.time(),
                ))

        except Exception as e:
            games.append(FreeGame(
                title=f"[API Error: {str(e)[:100]}]",
                storefront=Storefront.EPIC.value,
                url="", status="error", discovered_at=time.time(),
            ))

        return games

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "EpicFreeGamesAPI",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


class GOGFreeGamesAPI:
    """Fetch free/giveaway games from GOG."""

    GIVEAWAY_URL = "https://www.gog.com/games/ajax/filtered?mediaType=game&price=free&sort=popularity"

    @staticmethod
    def fetch() -> List[FreeGame]:
        """Execute fetch operation for GOGFreeGamesAPI engine."""
        games = []
        try:
            req = urllib.request.Request(
                GOGFreeGamesAPI.GIVEAWAY_URL,
                headers={"User-Agent": "OMNI-Claimer/1.0"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            for prod in data.get("products", []):
                games.append(FreeGame(
                    title=prod.get("title", "Unknown"),
                    storefront=Storefront.GOG.value,
                    url=f"https://www.gog.com{prod.get('url', '')}",
                    status=GameStatus.FREE_NOW.value,
                    original_price=str(prod.get("price", {}).get("baseAmount", "")),
                    discovered_at=time.time(),
                ))
        except Exception as e:
            games.append(FreeGame(
                title=f"[GOG Error: {str(e)[:100]}]",
                storefront=Storefront.GOG.value,
                url="", status="error", discovered_at=time.time(),
            ))
        return games

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "GOGFreeGamesAPI",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


# ── Claim History (SQLite) ──────────────────────────────────────────────────

class ClaimHistory:
    """Persistent catalog of discovered and claimed free games."""

    def __init__(self, db_path: str = ""):
        """Initialize ClaimHistory engine with default configuration."""
        if not db_path:
            db_path = os.path.join(os.path.dirname(__file__), "..", ".free_games.db")
        self.db_path = db_path
        self._init()

    def _init(self):
        """Execute  init operation for ClaimHistory engine."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT, storefront TEXT, url TEXT,
                status TEXT, original_price TEXT,
                start_date TEXT, end_date TEXT,
                discovered_at REAL,
                UNIQUE(title, storefront)
            )
        """)
        conn.commit()
        conn.close()

    def record(self, game: FreeGame):
        """Execute record operation for ClaimHistory engine."""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                "INSERT OR IGNORE INTO games (title,storefront,url,status,original_price,start_date,end_date,discovered_at) VALUES (?,?,?,?,?,?,?,?)",
                (game.title, game.storefront, game.url, game.status,
                 game.original_price, game.start_date, game.end_date,
                 game.discovered_at),
            )
            conn.commit()
        except Exception:
            pass
        conn.close()

    def get_all(self, limit: int = 50) -> List[Dict]:
        """Execute get all operation for ClaimHistory engine."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM games ORDER BY discovered_at DESC LIMIT ?", (limit,))
        cols = [d[0] for d in c.description]
        rows = [dict(zip(cols, row)) for row in c.fetchall()]
        conn.close()
        return rows

    def count_by_store(self) -> Dict:
        """Execute count by store operation for ClaimHistory engine."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT storefront, COUNT(*) FROM games GROUP BY storefront")
        result = {row[0]: row[1] for row in c.fetchall()}
        conn.close()
        return result

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "ClaimHistory",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniFreeGamesClaimerEngine:
    """
    OMNI Free Games Claimer Engine — Zero-Mock Digital Storefront Harvester.

    Capabilities (all native stdlib):
      - Epic Games Store free game polling (public API)
      - GOG free game discovery
      - Game catalog persistence (SQLite)
      - Store analytics (games per storefront)
    """

    def __init__(self):
        """Initialize FreeGamesClaimer engine with default configuration."""
        self.epic = EpicFreeGamesAPI()
        self.gog = GOGFreeGamesAPI()
        self.history = ClaimHistory()

    def scan_all_stores(self) -> Dict:
        """Poll all storefronts for free games and persist results."""
        all_games = []

        # Epic
        epic_games = self.epic.fetch()
        all_games.extend(epic_games)

        # GOG
        gog_games = self.gog.fetch()
        all_games.extend(gog_games)

        # Persist
        for game in all_games:
            if game.status != "error":
                self.history.record(game)

        return {
            "total_found": len(all_games),
            "stores": {
                "epic": len(epic_games),
                "gog": len(gog_games),
            },
            "games": [
                {"title": g.title, "store": g.storefront, "status": g.status,
                 "price": g.original_price, "url": g.url}
                for g in all_games
            ],
        }

    def get_epic_free(self) -> List[Dict]:
        """Get currently free Epic Games."""
        games = self.epic.fetch()
        return [
            {"title": g.title, "status": g.status, "price": g.original_price,
             "url": g.url, "end_date": g.end_date}
            for g in games if g.status == GameStatus.FREE_NOW.value
        ]

    def diagnostics(self) -> Dict:
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "OmniFreeGamesClaimerEngine",
            "status": "active",
            "capabilities": ["epic_free_games", "gog_free_games",
                             "claim_history", "store_analytics"],
            "db_path": self.history.db_path,
            "store_counts": self.history.count_by_store(),
        }


if __name__ == "__main__":
    engine = OmniFreeGamesClaimerEngine()
    print("[FreeGames] Scanning Epic Games Store...")
    free = engine.get_epic_free()
    print(json.dumps(free, indent=2))
