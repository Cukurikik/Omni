"""
OmniAiDeadlinesEngine — AI Conference Deadline Tracker & Scheduler.

Studied from: paperswithcode/ai-deadlines (4.9k★)
Implements: Conference entry management, countdown computation,
iCal export, filtering by sub-category, and ranking by h-index.

OMNI Domain: compute/ (Python)
CODE RULE 001-005 compliant. Zero external dependencies (beyond stdlib).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any


ENGINE_VERSION: str = "1.1.0-omni"
ENGINE_NAME: str = "OmniAiDeadlinesEngine"


# ---------------------------------------------------------------------------
# Enums & Data Classes
# ---------------------------------------------------------------------------

class SubCategory(Enum):
    """AI conference sub-categories matching ai-deadlines taxonomy."""
    ML = "Machine Learning"
    CV = "Computer Vision"
    NLP = "Natural Language Processing"
    RO = "Robotics"
    SP = "Speech"
    DM = "Data Mining"
    AI = "Artificial Intelligence"
    CG = "Computer Graphics"
    HCI = "Human-Computer Interaction"
    IR = "Information Retrieval"


@dataclass
class ConferenceEntry:
    """A single conference deadline entry.

    Attributes:
        title: Short conference name (e.g. "NeurIPS").
        year: Conference year.
        id: Unique identifier slug.
        full_name: Full conference name.
        link: Conference website URL.
        deadline: Submission deadline as UTC datetime.
        timezone_str: Timezone string for display.
        place: Location of the conference.
        date_display: Human-readable date string (e.g. "Dec 2026").
        sub: Sub-category classification.
        hindex: Google Scholar h5-index.
        note: Optional additional notes.
    """
    title: str
    year: int
    id: str
    full_name: str
    link: str
    deadline: datetime
    timezone_str: str
    place: str
    date_display: str
    sub: SubCategory
    hindex: float = 0.0
    note: str = ""


@dataclass
class CountdownResult:
    """Result of a countdown computation for a single conference.

    Attributes:
        conference_id: The conference identifier.
        title: Short name.
        deadline: The deadline datetime.
        time_remaining: Timedelta until deadline (negative if passed).
        days_remaining: Integer days remaining.
        is_expired: Whether the deadline has passed.
        urgency: Urgency label string.
    """
    conference_id: str
    title: str
    deadline: datetime
    time_remaining: timedelta
    days_remaining: int
    is_expired: bool
    urgency: str


# ---------------------------------------------------------------------------
# Core Engine
# ---------------------------------------------------------------------------

class OmniAiDeadlinesEngine:
    """Production-grade AI conference deadline tracker engine.

    Provides conference management, countdown computation, iCal export,
    filtering by sub-category, and ranking by h-index. Inspired by the
    paperswithcode/ai-deadlines project.
    """

    def __init__(self) -> None:
        """Initialize OmniAiDeadlinesEngine."""
        self._conferences: Dict[str, ConferenceEntry] = {}
        self._version: str = ENGINE_VERSION
        self._name: str = ENGINE_NAME

    # -- Conference Management -----------------------------------------------

    def add_conference(self, entry: ConferenceEntry) -> None:
        """Add or update a conference entry.

        Args:
            entry: ConferenceEntry instance to register.
        """
        self._conferences[entry.id] = entry

    def remove_conference(self, conference_id: str) -> bool:
        """Remove a conference by ID.

        Args:
            conference_id: Unique conference identifier.

        Returns:
            True if removed, False if not found.
        """
        if conference_id in self._conferences:
            del self._conferences[conference_id]
            return True
        return False

    def get_conference(self, conference_id: str) -> Optional[ConferenceEntry]:
        """Retrieve a single conference by ID.

        Args:
            conference_id: Unique conference identifier.

        Returns:
            ConferenceEntry or None.
        """
        return self._conferences.get(conference_id)

    def list_conferences(self) -> List[ConferenceEntry]:
        """List all registered conferences.

        Returns:
            List of ConferenceEntry objects.
        """
        return list(self._conferences.values())

    # -- Countdown Computation -----------------------------------------------

    def compute_countdowns(
        self, now: Optional[datetime] = None
    ) -> List[CountdownResult]:
        """Compute countdowns for all registered conferences.

        Args:
            now: Reference time (defaults to current UTC time).

        Returns:
            List of CountdownResult sorted by deadline ascending.
        """
        if now is None:
            now = datetime.now(timezone.utc)

        results: List[CountdownResult] = []
        for entry in self._conferences.values():
            dl = entry.deadline
            if dl.tzinfo is None:
                dl = dl.replace(tzinfo=timezone.utc)
            remaining = dl - now
            days = remaining.days
            is_expired = remaining.total_seconds() <= 0

            if is_expired:
                urgency = "EXPIRED"
            elif days <= 3:
                urgency = "CRITICAL"
            elif days <= 14:
                urgency = "APPROACHING"
            elif days <= 30:
                urgency = "UPCOMING"
            else:
                urgency = "SAFE"

            results.append(CountdownResult(
                conference_id=entry.id,
                title=entry.title,
                deadline=dl,
                time_remaining=remaining,
                days_remaining=days,
                is_expired=is_expired,
                urgency=urgency,
            ))

        results.sort(key=lambda r: r.deadline)
        return results

    # -- iCal Export ---------------------------------------------------------

    def export_ical(self) -> str:
        """Export all conference deadlines as iCalendar (RFC 5545) string.

        Returns:
            iCal-formatted string with VEVENT for each conference.
        """
        lines: List[str] = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//OMNI//OmniAiDeadlinesEngine//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
        ]

        for entry in self._conferences.values():
            dl = entry.deadline
            if dl.tzinfo is None:
                dl = dl.replace(tzinfo=timezone.utc)
            dtstart = dl.strftime("%Y%m%dT%H%M%SZ")
            dtend = (dl + timedelta(hours=1)).strftime("%Y%m%dT%H%M%SZ")

            lines.extend([
                "BEGIN:VEVENT",
                f"DTSTART:{dtstart}",
                f"DTEND:{dtend}",
                f"SUMMARY:{entry.title} {entry.year} Deadline",
                f"DESCRIPTION:{entry.full_name}",
                f"LOCATION:{entry.place}",
                f"URL:{entry.link}",
                f"UID:{entry.id}@omni-ai-deadlines",
                "END:VEVENT",
            ])

        lines.append("END:VCALENDAR")
        return "\r\n".join(lines)

    # -- Filtering -----------------------------------------------------------

    def filter_by_sub(self, sub: SubCategory) -> List[ConferenceEntry]:
        """Filter conferences by sub-category.

        Args:
            sub: SubCategory enum value.

        Returns:
            List of matching ConferenceEntry objects.
        """
        return [e for e in self._conferences.values() if e.sub == sub]

    def filter_by_year(self, year: int) -> List[ConferenceEntry]:
        """Filter conferences by year.

        Args:
            year: Target year.

        Returns:
            List of matching ConferenceEntry objects.
        """
        return [e for e in self._conferences.values() if e.year == year]

    # -- Ranking -------------------------------------------------------------

    def rank_by_hindex(self, descending: bool = True) -> List[ConferenceEntry]:
        """Rank conferences by h5-index.

        Args:
            descending: If True, highest h-index first.

        Returns:
            Sorted list of ConferenceEntry objects.
        """
        return sorted(
            self._conferences.values(),
            key=lambda e: e.hindex,
            reverse=descending,
        )

    def rank_by_deadline(self) -> List[ConferenceEntry]:
        """Rank conferences by deadline (soonest first).

        Returns:
            Sorted list of ConferenceEntry objects.
        """
        return sorted(self._conferences.values(), key=lambda e: e.deadline)

    # -- Health / Diagnostics ------------------------------------------------

    def health(self) -> Dict[str, Any]:
        """Return engine health diagnostics.

        Returns:
            Dictionary with engine status information.
        """
        return {
            "engine": self._name,
            "version": self._version,
            "status": "operational",
            "conference_count": len(self._conferences),
            "capabilities": [
                "add_conference", "remove_conference", "compute_countdowns",
                "export_ical", "filter_by_sub", "filter_by_year",
                "rank_by_hindex", "rank_by_deadline",
            ],
        }

    # Legacy alias for diagnostics
    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniAiDeadlinesEngine."""
        return self.health()

    # -- Legacy API (Batch 9/10 backward compatibility) -----------------------

    def compute_decay_matrix(self, current_t: float, deadlines):
        """Compute time-decay urgency matrix for deadline timestamps.

        For each deadline:
          - If deadline <= current_t: urgency = 1.0, state = "EXPIRED/REACHED"
          - Otherwise: urgency = exp(-alpha * (deadline - current_t)), state is
            one of "CRITICAL", "APPROACHING", "UPCOMING", "SAFE".

        Args:
            current_t: Current timestamp (float).
            deadlines: Array-like of deadline timestamps.

        Returns:
            Result wrapping dict with 'urgency_matrix' and 'states'.
        """
        import numpy as _np
        try:
            dl = _np.asarray(deadlines, dtype=_np.float64)
            urgency = _np.zeros_like(dl)
            states = []
            alpha = 0.005  # decay rate

            for i, d in enumerate(dl):
                diff = d - current_t
                if diff <= 0:
                    urgency[i] = 1.0
                    states.append("EXPIRED/REACHED")
                else:
                    urgency[i] = float(_np.exp(-alpha * diff))
                    if diff <= 10:
                        states.append("CRITICAL")
                    elif diff <= 50:
                        states.append("APPROACHING")
                    elif diff <= 200:
                        states.append("UPCOMING")
                    else:
                        states.append("SAFE")

            return _Result(value={"urgency_matrix": urgency, "states": states})
        except Exception as e:
            return _Result(error=f"Decay matrix computation error: {str(e)}")


# ---------------------------------------------------------------------------
# Legacy Result class (backward-compatible with Batch 9/10 tests)
# ---------------------------------------------------------------------------

class _Result:
    """Monadic result pattern for legacy compatibility."""
    def __init__(self, value=None, error=None):
        """Initialize _Result."""
        self.value = value
        self.error = error
        self.is_ok = error is None

    def unwrap(self):
        """Unwrap the value or raise on error."""
        if not self.is_ok:
            raise RuntimeError(self.error)
        return self.value
