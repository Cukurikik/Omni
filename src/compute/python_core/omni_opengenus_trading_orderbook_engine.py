"""OmniOpenGenusTradingOrderBookEngine — Order Book Matching Engine.

Inspired by OpenGenus/trading-app-in-cpp: a trading application
implementing order book mechanics, bid-ask spread computation,
and price-time priority matching.

Algorithmic Primitive:
    Maintain a sorted order book with bids (descending by price) and
    asks (ascending by price). Match incoming orders against the book
    using price-time priority. Compute bid-ask spread and mid-price.
"""
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from __future__ import annotations
import sys, os
from src.compute.python_core.omni_base_engine import Result, Ok, Err
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))


class OmniOpenGenusTradingOrderBookEngine:
    """Production-grade order book matching engine with price-time priority."""

    @staticmethod
    def diagnostics() -> dict:
        """Return engine metadata for OMNI ecosystem health checks."""
        return {
            "engine": "OmniOpenGenusTradingOrderBookEngine",
            "version": "1.0.0",
            "primitive": "price_time_priority_order_matching",
            "monadic_enforcement": True,
            "source_repo": "OpenGenus/trading-app-in-cpp",
        }

    @staticmethod
    def compute_spread(bids: list[dict], asks: list[dict]) -> Result:
        """Compute the bid-ask spread and mid-price.

        Args:
            bids: List of bid orders, each with 'price' (float) and 'qty' (int).
            asks: List of ask orders, each with 'price' (float) and 'qty' (int).

        Returns:
            Result[dict, Exception]: dict with 'best_bid', 'best_ask',
            'spread', 'mid_price'. Returns Err if either side is empty.
        """
        if not isinstance(bids, list) or not isinstance(asks, list):
            return Err(Exception("bids and asks must be lists"))
        if len(bids) == 0:
            return Err(Exception("No bids in order book"))
        if len(asks) == 0:
            return Err(Exception("No asks in order book"))

        best_bid = max(b["price"] for b in bids)
        best_ask = min(a["price"] for a in asks)
        spread = round(best_ask - best_bid, 6)
        mid_price = round((best_bid + best_ask) / 2.0, 6)

        return Ok({
            "best_bid": best_bid,
            "best_ask": best_ask,
            "spread": spread,
            "mid_price": mid_price,
        })

    @staticmethod
    def match_order(
        order: dict,
        bids: list[dict],
        asks: list[dict],
    ) -> Result:
        """Match an incoming order against the order book.

        Uses price-time priority: best price first, then earliest timestamp.

        Args:
            order: dict with 'side' ('buy'|'sell'), 'price' (float),
                   'qty' (int), 'timestamp' (int).
            bids: Existing bid orders (each with price, qty, timestamp).
            asks: Existing ask orders (each with price, qty, timestamp).

        Returns:
            Result[dict, Exception]: dict with 'fills' (list of fill dicts),
            'remaining_qty' (unfilled quantity), 'fully_filled' (bool).
        """
        if not isinstance(order, dict):
            return Err(Exception("order must be a dict"))
        side = order.get("side")
        if side not in ("buy", "sell"):
            return Err(Exception("order side must be 'buy' or 'sell'"))
        if order.get("qty", 0) <= 0:
            return Err(Exception("order qty must be positive"))
        if order.get("price", 0) <= 0:
            return Err(Exception("order price must be positive"))

        remaining = order["qty"]
        fills: list[dict] = []

        if side == "buy":
            # Match against asks (ascending price, then timestamp)
            sorted_asks = sorted(asks, key=lambda a: (a["price"], a.get("timestamp", 0)))
            for ask in sorted_asks:
                if remaining <= 0:
                    break
                if ask["price"] <= order["price"]:
                    fill_qty = min(remaining, ask["qty"])
                    fills.append({
                        "price": ask["price"],
                        "qty": fill_qty,
                        "counterparty_timestamp": ask.get("timestamp", 0),
                    })
                    remaining -= fill_qty
        else:
            # Match against bids (descending price, then timestamp)
            sorted_bids = sorted(bids, key=lambda b: (-b["price"], b.get("timestamp", 0)))
            for bid in sorted_bids:
                if remaining <= 0:
                    break
                if bid["price"] >= order["price"]:
                    fill_qty = min(remaining, bid["qty"])
                    fills.append({
                        "price": bid["price"],
                        "qty": fill_qty,
                        "counterparty_timestamp": bid.get("timestamp", 0),
                    })
                    remaining -= fill_qty

        return Ok({
            "fills": fills,
            "remaining_qty": remaining,
            "fully_filled": remaining == 0,
        })

    @staticmethod
    def compute_vwap(trades: list[dict]) -> Result:
        """Compute Volume-Weighted Average Price from a list of trades.

        Args:
            trades: List of trade dicts, each with 'price' and 'qty'.

        Returns:
            Result[float, Exception]: The VWAP value.
        """
        if not isinstance(trades, list) or len(trades) == 0:
            return Err(Exception("trades must be a non-empty list"))

        total_value = 0.0
        total_volume = 0

        for t in trades:
            if t.get("qty", 0) <= 0 or t.get("price", 0) <= 0:
                return Err(Exception("Each trade must have positive price and qty"))
            total_value += t["price"] * t["qty"]
            total_volume += t["qty"]

        return Ok(round(total_value / total_volume, 6))
