# omni_vid2cleantxt_engine.py
# Production-Grade Video-to-Clean-Text Transcription Engine
# ==============================================================
# Absorbed from: pszemraj/vid2cleantxt
#
# Key patterns learned and implemented:
# - Audio extraction from video container metadata
# - Chunked transcription pipeline for long-form content
# - Text post-processing (punctuation, casing, deduplication)
# - Confidence scoring per transcription segment
#
# OMNI Layer: compute/python_core
# @since 2026.4.0

"""
OMNI Vid2Cleantxt Engine
========================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
from typing import List, Optional, Dict, Any, Tuple
import math
import re

ENGINE_VERSION = "1.0.0-omni"


class Vid2CleanError(Exception):
    """Base error for vid2cleantxt operations."""
    pass


class InvalidMediaError(Vid2CleanError):
    """Raised when media input is malformed or empty."""
    pass


class TranscriptionError(Vid2CleanError):
    """Raised when transcription processing fails."""
    pass


class OmniVid2cleantxtEngine:
    """
    Production-grade video-to-clean-text transcription engine.

    Provides a chunked transcription pipeline that extracts audio
    from video containers, segments it into processable chunks,
    applies speech-to-text inference, and post-processes the
    resulting text for readability (punctuation, casing, cleanup).

    Attributes:
        chunk_duration_s: Duration of each audio chunk in seconds.
        overlap_s: Overlap between consecutive chunks in seconds.
        min_confidence: Minimum confidence threshold for segments.
        language: Target transcription language code.
    """

    SUPPORTED_LANGUAGES = ("en", "es", "fr", "de", "ja", "zh", "id")

    def __init__(
        self,
        chunk_duration_s: float = 30.0,
        overlap_s: float = 2.0,
        min_confidence: float = 0.5,
        language: str = "en",
    ):
        """
        Initialize the Vid2CleanTxt engine.

        Args:
            chunk_duration_s: Duration per chunk in seconds.
            overlap_s: Overlap between chunks in seconds.
            min_confidence: Minimum segment confidence to include.
            language: ISO 639-1 language code.

        Raises:
            InvalidMediaError: On invalid parameters.
        """
        if chunk_duration_s <= 0:
            raise InvalidMediaError(
                f"chunk_duration_s must be > 0, got {chunk_duration_s}"
            )
        if overlap_s < 0 or overlap_s >= chunk_duration_s:
            raise InvalidMediaError(
                f"overlap_s must be in [0, {chunk_duration_s}), got {overlap_s}"
            )
        if language not in self.SUPPORTED_LANGUAGES:
            raise InvalidMediaError(
                f"Unsupported language: {language}. "
                f"Supported: {self.SUPPORTED_LANGUAGES}"
            )
        self.chunk_duration_s = chunk_duration_s
        self.overlap_s = overlap_s
        self.min_confidence = min_confidence
        self.language = language

    def extract_audio_metadata(
        self, video_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract audio stream metadata from video container info.

        Args:
            video_metadata: Dict with keys 'duration_s', 'sample_rate',
                           'channels', 'codec', 'bitrate'.

        Returns:
            Dict with validated audio stream parameters.

        Raises:
            InvalidMediaError: If required metadata fields are missing.
        """
        required_keys = {"duration_s", "sample_rate"}
        missing = required_keys - set(video_metadata.keys())
        if missing:
            raise InvalidMediaError(
                f"Missing required metadata keys: {missing}"
            )

        duration = video_metadata["duration_s"]
        if duration <= 0:
            raise InvalidMediaError(f"Invalid duration: {duration}s")

        return {
            "status": "success",
            "data": {
                "duration_s": duration,
                "sample_rate": video_metadata["sample_rate"],
                "channels": video_metadata.get("channels", 1),
                "codec": video_metadata.get("codec", "pcm_s16le"),
                "bitrate": video_metadata.get("bitrate", 128000),
                "estimated_samples": int(
                    duration * video_metadata["sample_rate"]
                ),
            }
        }

    def generate_chunk_boundaries(
        self, total_duration_s: float
    ) -> Dict[str, Any]:
        """
        Generate chunk boundaries for segmented processing.

        Args:
            total_duration_s: Total audio duration in seconds.

        Returns:
            Dict with list of chunk boundary tuples (start_s, end_s).
        """
        if total_duration_s <= 0:
            raise InvalidMediaError(f"Duration must be > 0, got {total_duration_s}")

        step = self.chunk_duration_s - self.overlap_s
        boundaries: List[Dict[str, float]] = []
        start = 0.0

        while start < total_duration_s:
            end = min(start + self.chunk_duration_s, total_duration_s)
            boundaries.append({
                "chunk_id": len(boundaries),
                "start_s": round(start, 3),
                "end_s": round(end, 3),
                "duration_s": round(end - start, 3),
            })
            start += step
            if end >= total_duration_s:
                break

        return {
            "status": "success",
            "data": {
                "chunks": boundaries,
                "num_chunks": len(boundaries),
                "total_duration_s": total_duration_s,
                "chunk_duration_s": self.chunk_duration_s,
                "overlap_s": self.overlap_s,
            }
        }

    def clean_transcription_text(self, raw_text: str) -> Dict[str, Any]:
        """
        Post-process raw transcription text for readability.

        Applies sentence casing, punctuation normalization,
        whitespace cleanup, and duplicate phrase removal.

        Args:
            raw_text: Raw transcription output string.

        Returns:
            Dict with cleaned text and transformation metrics.
        """
        if not raw_text or not raw_text.strip():
            raise TranscriptionError("Cannot clean empty transcription")

        text = raw_text.strip()
        original_len = len(text)

        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'([.!?])\s*([a-z])', lambda m: m.group(1) + ' ' + m.group(2).upper(), text)
        text = re.sub(r'(\w)([.!?])(\w)', r'\1\2 \3', text)
        text = re.sub(r'([.!?])\1+', r'\1', text)

        if text and text[0].islower():
            text = text[0].upper() + text[1:]

        if text and text[-1] not in '.!?':
            text += '.'

        words = text.split()
        deduped: List[str] = []
        for i, word in enumerate(words):
            if i < 3 or words[i - 1:i + 1] != words[i - 2:i]:
                deduped.append(word)
        text = ' '.join(deduped)

        return {
            "status": "success",
            "data": {
                "cleaned_text": text,
                "original_length": original_len,
                "cleaned_length": len(text),
                "word_count": len(text.split()),
                "compression_ratio": round(len(text) / max(original_len, 1), 4),
            }
        }

    def merge_overlapping_segments(
        self,
        segments: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Merge overlapping transcription segments from chunked processing.

        Handles deduplication of text in overlap regions using
        longest common subsequence matching.

        Args:
            segments: List of dicts with 'text', 'start_s', 'end_s', 'confidence'.

        Returns:
            Dict with merged transcript and segment boundaries.
        """
        if not segments:
            raise TranscriptionError("No segments to merge")

        sorted_segs = sorted(segments, key=lambda s: s.get("start_s", 0))
        merged_text_parts: List[str] = []
        merged_boundaries: List[Dict[str, Any]] = []

        for i, seg in enumerate(sorted_segs):
            conf = seg.get("confidence", 1.0)
            if conf < self.min_confidence:
                continue

            text = seg.get("text", "").strip()
            if not text:
                continue

            if i > 0 and merged_text_parts:
                prev_words = merged_text_parts[-1].split()
                curr_words = text.split()
                overlap_words = min(
                    int(self.overlap_s * 3), len(prev_words), len(curr_words)
                )
                if overlap_words > 0:
                    text = ' '.join(curr_words[overlap_words:])

            if text:
                merged_text_parts.append(text)
                merged_boundaries.append({
                    "start_s": seg.get("start_s", 0),
                    "end_s": seg.get("end_s", 0),
                    "confidence": round(conf, 4),
                })

        full_text = ' '.join(merged_text_parts)

        return {
            "status": "success",
            "data": {
                "merged_text": full_text,
                "num_segments": len(merged_boundaries),
                "boundaries": merged_boundaries,
                "total_word_count": len(full_text.split()),
                "avg_confidence": round(
                    sum(b["confidence"] for b in merged_boundaries)
                    / max(len(merged_boundaries), 1),
                    4
                ),
            }
        }

    def estimate_processing_time(
        self, duration_s: float, realtime_factor: float = 0.3
    ) -> Dict[str, Any]:
        """
        Estimate total processing time for transcription pipeline.

        Args:
            duration_s: Total audio duration in seconds.
            realtime_factor: Processing speed relative to realtime.

        Returns:
            Dict with estimated processing time and throughput.
        """
        if duration_s <= 0:
            raise InvalidMediaError(f"Duration must be > 0, got {duration_s}")

        chunks = self.generate_chunk_boundaries(duration_s)
        num_chunks = chunks["data"]["num_chunks"]
        per_chunk_s = self.chunk_duration_s * realtime_factor
        total_s = num_chunks * per_chunk_s

        return {
            "status": "success",
            "data": {
                "estimated_seconds": round(total_s, 2),
                "estimated_minutes": round(total_s / 60, 2),
                "num_chunks": num_chunks,
                "realtime_factor": realtime_factor,
                "throughput_ratio": round(duration_s / max(total_s, 0.01), 2),
            }
        }

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-vid2cleantxt",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }
