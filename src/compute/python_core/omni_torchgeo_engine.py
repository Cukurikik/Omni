"""
OMNI TorchGeo Engine — Geospatial data processing and remote sensing primitives.

Assimilated from: torchgeo/torchgeo (2.8k ★)
Implements core geospatial data operations:
  - Spectral indices: NDVI, NDWI, NBR, NDBI, NDSI, SAVI, EVI, GNDVI
  - Coordinate transforms: lat/lon ↔ UTM, Haversine distance
  - Raster sampling: grid, random crop, sliding window
  - Band math: normalized difference, ratio, tri-band
  - Temporal compositing: median/max pixel across time series
  - Zonal statistics: per-zone mean, std, min, max
  - Cloud masking: QA-band based mask generation

OMNI Domain: compute/ (Python)
CODE RULE 001-005 compliant. Only numpy dependency.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


ENGINE_VERSION: str = "1.0.0-omni"
ENGINE_NAME: str = "OmniTorchGeoEngine"

_EPSILON: float = 1e-10


# ---------------------------------------------------------------------------
# Monadic Result
# ---------------------------------------------------------------------------

class Result:
    """Monadic Result type for error handling."""
    pass


class Ok(Result):
    """Monadic Ok result type."""
    def __init__(self, value: Any) -> None:
        """Initialize Ok."""
        self.value = value


class Err(Result):
    """Monadic Err result type."""
    def __init__(self, error: str) -> None:
        """Initialize Err."""
        self.error = error


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class OmniTorchGeoEngine:
    """Production-grade geospatial data processing engine.

    Provides remote sensing and geospatial analysis primitives:
      - Multi-band spectral index computation
      - Geographic coordinate transformations
      - Raster sampling strategies
      - Temporal image compositing
      - Zonal statistics
      - Cloud/shadow masking

    @since 1.0.0
    @tags ["geospatial", "remote-sensing", "gis", "spectral-indices", "compute"]
    """

    VERSION = ENGINE_VERSION
    ENGINE_ID = ENGINE_NAME

    def __init__(self) -> None:
        """Initialize OmniTorchGeoEngine."""
        self._omni_version: str = "3.0.0-OMNI-NEXUS"

    def diagnostics(self) -> Result:
        """Return engine health diagnostics."""
        return Ok({
            "engine": self.ENGINE_ID,
            "version": self.VERSION,
            "status": "operational",
            "capabilities": [
                "ndvi", "ndwi", "nbr", "ndbi", "ndsi", "savi", "evi",
                "haversine", "utm_convert", "grid_sample",
                "temporal_composite", "zonal_stats", "cloud_mask",
            ],
        })

    # -----------------------------------------------------------------
    # 1. SPECTRAL INDICES
    # -----------------------------------------------------------------

    def normalized_difference(self, band_a: np.ndarray, band_b: np.ndarray) -> Result:
        """Compute Normalized Difference Index: (A - B) / (A + B).

        Generic formula used by NDVI, NDWI, NBR, NDBI, NDSI, etc.

        @param band_a: 2D array for the reference band.
        @param band_b: 2D array for the difference band.
        @returns Result containing 2D NDI values in [-1, 1].
        """
        if band_a.shape != band_b.shape:
            return Err("Band shapes must match.")
        a = band_a.astype(np.float64)
        b = band_b.astype(np.float64)
        ndi = (a - b) / (a + b + _EPSILON)
        return Ok(ndi)

    def compute_ndvi(self, nir: np.ndarray, red: np.ndarray) -> Result:
        """Compute Normalized Difference Vegetation Index.

        NDVI = (NIR - Red) / (NIR + Red)

        @param nir: Near-infrared band.
        @param red: Red band.
        @returns Result containing 2D NDVI.
        """
        return self.normalized_difference(nir, red)

    def compute_ndwi(self, green: np.ndarray, nir: np.ndarray) -> Result:
        """Compute Normalized Difference Water Index.

        NDWI = (Green - NIR) / (Green + NIR)

        @param green: Green band.
        @param nir: Near-infrared band.
        @returns Result containing 2D NDWI.
        """
        return self.normalized_difference(green, nir)

    def compute_nbr(self, nir: np.ndarray, swir: np.ndarray) -> Result:
        """Compute Normalized Burn Ratio.

        NBR = (NIR - SWIR) / (NIR + SWIR)

        @param nir: Near-infrared band.
        @param swir: Short-wave infrared band.
        @returns Result containing 2D NBR.
        """
        return self.normalized_difference(nir, swir)

    def compute_ndbi(self, swir: np.ndarray, nir: np.ndarray) -> Result:
        """Compute Normalized Difference Built-up Index.

        NDBI = (SWIR - NIR) / (SWIR + NIR)

        @param swir: Short-wave infrared band.
        @param nir: Near-infrared band.
        @returns Result containing 2D NDBI.
        """
        return self.normalized_difference(swir, nir)

    def compute_ndsi(self, green: np.ndarray, swir: np.ndarray) -> Result:
        """Compute Normalized Difference Snow Index.

        NDSI = (Green - SWIR) / (Green + SWIR)

        @param green: Green band.
        @param swir: Short-wave infrared band.
        @returns Result containing 2D NDSI.
        """
        return self.normalized_difference(green, swir)

    def compute_savi(
        self, nir: np.ndarray, red: np.ndarray, L: float = 0.5
    ) -> Result:
        """Compute Soil-Adjusted Vegetation Index.

        SAVI = ((NIR - Red) / (NIR + Red + L)) * (1 + L)

        @param nir: Near-infrared band.
        @param red: Red band.
        @param L: Soil brightness correction factor (default 0.5).
        @returns Result containing 2D SAVI.
        """
        if nir.shape != red.shape:
            return Err("Band shapes must match.")
        n = nir.astype(np.float64)
        r = red.astype(np.float64)
        savi = ((n - r) / (n + r + L + _EPSILON)) * (1 + L)
        return Ok(savi)

    def compute_evi(
        self,
        nir: np.ndarray,
        red: np.ndarray,
        blue: np.ndarray,
        G: float = 2.5,
        C1: float = 6.0,
        C2: float = 7.5,
        L: float = 1.0,
    ) -> Result:
        """Compute Enhanced Vegetation Index.

        EVI = G * (NIR - Red) / (NIR + C1*Red - C2*Blue + L)

        @param nir: Near-infrared band.
        @param red: Red band.
        @param blue: Blue band.
        @returns Result containing 2D EVI.
        """
        if nir.shape != red.shape or nir.shape != blue.shape:
            return Err("All band shapes must match.")
        n = nir.astype(np.float64)
        r = red.astype(np.float64)
        b = blue.astype(np.float64)
        denom = n + C1 * r - C2 * b + L + _EPSILON
        evi = G * (n - r) / denom
        return Ok(evi)

    def compute_gndvi(self, nir: np.ndarray, green: np.ndarray) -> Result:
        """Compute Green Normalized Difference Vegetation Index.

        GNDVI = (NIR - Green) / (NIR + Green)

        @param nir: Near-infrared band.
        @param green: Green band.
        @returns Result containing 2D GNDVI.
        """
        return self.normalized_difference(nir, green)

    # -----------------------------------------------------------------
    # 2. COORDINATE TRANSFORMS
    # -----------------------------------------------------------------

    def haversine_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> Result:
        """Compute great-circle distance between two points using Haversine formula.

        @param lat1: Latitude of point 1 (degrees).
        @param lon1: Longitude of point 1 (degrees).
        @param lat2: Latitude of point 2 (degrees).
        @param lon2: Longitude of point 2 (degrees).
        @returns Result containing distance in meters.
        """
        R = 6371000.0  # Earth radius in meters
        φ1, φ2 = math.radians(lat1), math.radians(lat2)
        Δφ = math.radians(lat2 - lat1)
        Δλ = math.radians(lon2 - lon1)
        a = math.sin(Δφ / 2) ** 2 + math.cos(φ1) * math.cos(φ2) * math.sin(Δλ / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return Ok(R * c)

    def latlon_to_utm(self, lat: float, lon: float) -> Result:
        """Convert latitude/longitude to UTM coordinates (simplified).

        Uses WGS84 ellipsoid. Returns easting, northing, zone number.

        @param lat: Latitude in degrees.
        @param lon: Longitude in degrees.
        @returns Result containing dict with 'easting', 'northing', 'zone'.
        """
        if lat < -80 or lat > 84:
            return Err("Latitude out of UTM range [-80, 84].")

        zone = int((lon + 180) / 6) + 1

        # WGS84 parameters
        a = 6378137.0
        f = 1 / 298.257223563
        e = math.sqrt(2 * f - f ** 2)

        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        lon0_rad = math.radians((zone - 1) * 6 - 180 + 3)

        N = a / math.sqrt(1 - e ** 2 * math.sin(lat_rad) ** 2)
        T = math.tan(lat_rad) ** 2
        C = (e ** 2 / (1 - e ** 2)) * math.cos(lat_rad) ** 2
        A = math.cos(lat_rad) * (lon_rad - lon0_rad)

        # Simplified M (meridional arc)
        e2 = e ** 2
        M = a * (
            (1 - e2 / 4 - 3 * e2 ** 2 / 64) * lat_rad
            - (3 * e2 / 8 + 3 * e2 ** 2 / 32) * math.sin(2 * lat_rad)
            + (15 * e2 ** 2 / 256) * math.sin(4 * lat_rad)
        )

        k0 = 0.9996
        easting = k0 * N * (A + (1 - T + C) * A ** 3 / 6) + 500000
        northing = k0 * (M + N * math.tan(lat_rad) * (A ** 2 / 2 + (5 - T + 9 * C) * A ** 4 / 24))
        if lat < 0:
            northing += 10000000

        return Ok({"easting": easting, "northing": northing, "zone": zone})

    def bounding_box_area(
        self, lat_min: float, lon_min: float, lat_max: float, lon_max: float
    ) -> Result:
        """Approximate area of geographic bounding box in km².

        @param lat_min: Minimum latitude.
        @param lon_min: Minimum longitude.
        @param lat_max: Maximum latitude.
        @param lon_max: Maximum longitude.
        @returns Result containing area in square kilometers.
        """
        if lat_min >= lat_max or lon_min >= lon_max:
            return Err("Invalid bounding box.")

        mid_lat = (lat_min + lat_max) / 2
        km_per_deg_lat = 111.32  # approximately constant
        km_per_deg_lon = 111.32 * math.cos(math.radians(mid_lat))

        width_km = (lon_max - lon_min) * km_per_deg_lon
        height_km = (lat_max - lat_min) * km_per_deg_lat
        return Ok(width_km * height_km)

    # -----------------------------------------------------------------
    # 3. RASTER SAMPLING
    # -----------------------------------------------------------------

    def grid_sample(
        self, raster: np.ndarray, patch_size: int, stride: int
    ) -> Result:
        """Extract patches from raster using sliding window.

        @param raster: 2D or 3D (C, H, W) raster array.
        @param patch_size: Size of square patches.
        @param stride: Step between patches.
        @returns Result containing list of patches and their (row, col) positions.
        """
        if raster.ndim == 2:
            h, w = raster.shape
        elif raster.ndim == 3:
            _, h, w = raster.shape
        else:
            return Err("raster must be 2D or 3D.")

        if patch_size < 1 or stride < 1:
            return Err("patch_size and stride must be >= 1.")

        patches = []
        positions = []
        for i in range(0, h - patch_size + 1, stride):
            for j in range(0, w - patch_size + 1, stride):
                if raster.ndim == 2:
                    patch = raster[i:i + patch_size, j:j + patch_size]
                else:
                    patch = raster[:, i:i + patch_size, j:j + patch_size]
                patches.append(patch)
                positions.append((i, j))

        return Ok({"patches": patches, "positions": positions, "n_patches": len(patches)})

    def random_geo_crop(
        self, raster: np.ndarray, crop_size: int, n_crops: int, seed: int = 42
    ) -> Result:
        """Extract random crops from raster.

        @param raster: 2D array.
        @param crop_size: Size of square crop.
        @param n_crops: Number of random crops.
        @param seed: Random seed.
        @returns Result containing list of crops.
        """
        if raster.ndim != 2:
            return Err("raster must be 2D.")
        h, w = raster.shape
        if crop_size > h or crop_size > w:
            return Err("crop_size larger than raster.")

        rng = np.random.RandomState(seed)
        crops = []
        for _ in range(n_crops):
            i = rng.randint(0, h - crop_size + 1)
            j = rng.randint(0, w - crop_size + 1)
            crops.append(raster[i:i + crop_size, j:j + crop_size])
        return Ok(crops)

    # -----------------------------------------------------------------
    # 4. TEMPORAL COMPOSITING
    # -----------------------------------------------------------------

    def median_composite(self, time_series: np.ndarray) -> Result:
        """Compute per-pixel median composite across time dimension.

        @param time_series: 3D array (T, H, W) — T temporal frames.
        @returns Result containing 2D median composite.
        """
        if time_series.ndim != 3:
            return Err("time_series must be 3D (T, H, W).")
        return Ok(np.median(time_series, axis=0))

    def max_composite(self, time_series: np.ndarray) -> Result:
        """Compute per-pixel max composite (e.g., maximum NDVI).

        @param time_series: 3D array (T, H, W).
        @returns Result containing 2D max composite.
        """
        if time_series.ndim != 3:
            return Err("time_series must be 3D (T, H, W).")
        return Ok(np.max(time_series, axis=0))

    # -----------------------------------------------------------------
    # 5. ZONAL STATISTICS
    # -----------------------------------------------------------------

    def zonal_stats(self, raster: np.ndarray, zones: np.ndarray) -> Result:
        """Compute statistics per zone (segment/polygon).

        @param raster: 2D value raster.
        @param zones: 2D integer zone labels (same shape as raster).
        @returns Result containing dict mapping zone_id → {mean, std, min, max, count}.
        """
        if raster.shape != zones.shape or raster.ndim != 2:
            return Err("raster and zones must be 2D with same shape.")

        unique_zones = np.unique(zones)
        stats = {}
        for z in unique_zones:
            mask = zones == z
            vals = raster[mask]
            if len(vals) == 0:
                continue
            stats[int(z)] = {
                "mean": float(np.mean(vals)),
                "std": float(np.std(vals)),
                "min": float(np.min(vals)),
                "max": float(np.max(vals)),
                "count": int(len(vals)),
            }
        return Ok(stats)

    # -----------------------------------------------------------------
    # 6. CLOUD MASKING
    # -----------------------------------------------------------------

    def cloud_mask_from_qa(
        self, qa_band: np.ndarray, cloud_bit: int = 3, shadow_bit: int = 4
    ) -> Result:
        """Generate cloud/shadow mask from QA bit-packed band.

        Checks if specified bits are set in the QA band.

        @param qa_band: 2D integer QA band (e.g., Landsat QA_PIXEL).
        @param cloud_bit: Bit position for cloud flag.
        @param shadow_bit: Bit position for cloud shadow flag.
        @returns Result containing 2D binary mask (1=clear, 0=cloud/shadow).
        """
        if qa_band.ndim != 2:
            return Err("qa_band must be 2D.")

        cloud_mask = (qa_band >> cloud_bit) & 1
        shadow_mask = (qa_band >> shadow_bit) & 1
        clear = ((cloud_mask == 0) & (shadow_mask == 0)).astype(np.uint8)
        return Ok(clear)

    def apply_cloud_mask(
        self, raster: np.ndarray, mask: np.ndarray, fill_value: float = np.nan
    ) -> Result:
        """Apply cloud mask to raster, setting cloudy pixels to fill value.

        @param raster: 2D raster.
        @param mask: 2D binary mask (1=clear, 0=masked).
        @param fill_value: Value for masked pixels.
        @returns Result containing masked raster.
        """
        if raster.shape != mask.shape:
            return Err("Shape mismatch.")
        result = raster.astype(np.float64).copy()
        result[mask == 0] = fill_value
        return Ok(result)
