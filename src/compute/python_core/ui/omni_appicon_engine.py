ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI APPICON ENGINE — App Icon Generation & Asset Pipeline
# ===========================================================================
# Source Paradigm: https://github.com/Nonchalant/AppIcon
# Domain Layer  : Mobile (iOS/Android App Icon Management)
# Zero-Mock     : 100% Native — os, json, subprocess, hashlib
# ===========================================================================
"""
AppIcon teaches us:
  1. Single source image → multi-resolution icon generation
  2. iOS icon size catalog (20pt-1024pt, @1x/@2x/@3x)
  3. Android adaptive icon specifications (mipmap-mdpi to xxxhdpi)
  4. Contents.json (Xcode asset catalog) generation
  5. Image resizing pipeline
  6. Rounding/masking for platform compliance

This engine distills those paradigms into OMNI-native Python for
generating complete icon sets from a single source image using ffmpeg.
"""

import hashlib
import json
import os
import subprocess
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ── Data Models ──────────────────────────────────────────────────────────────

@dataclass
class IconSpec:
    name: str
    size: int           # pixels
    scale: str = "1x"   # "1x", "2x", "3x"
    idiom: str = ""     # "iphone", "ipad", "universal", "android"
    platform: str = ""  # "ios", "android", "web"


# ── Icon Size Catalogs ────────────────────────────────────────────────────

IOS_ICONS: List[IconSpec] = [
    IconSpec("iphone-20@2x", 40, "2x", "iphone", "ios"),
    IconSpec("iphone-20@3x", 60, "3x", "iphone", "ios"),
    IconSpec("iphone-29@2x", 58, "2x", "iphone", "ios"),
    IconSpec("iphone-29@3x", 87, "3x", "iphone", "ios"),
    IconSpec("iphone-40@2x", 80, "2x", "iphone", "ios"),
    IconSpec("iphone-40@3x", 120, "3x", "iphone", "ios"),
    IconSpec("iphone-60@2x", 120, "2x", "iphone", "ios"),
    IconSpec("iphone-60@3x", 180, "3x", "iphone", "ios"),
    IconSpec("ipad-20@1x", 20, "1x", "ipad", "ios"),
    IconSpec("ipad-20@2x", 40, "2x", "ipad", "ios"),
    IconSpec("ipad-29@1x", 29, "1x", "ipad", "ios"),
    IconSpec("ipad-29@2x", 58, "2x", "ipad", "ios"),
    IconSpec("ipad-40@1x", 40, "1x", "ipad", "ios"),
    IconSpec("ipad-40@2x", 80, "2x", "ipad", "ios"),
    IconSpec("ipad-76@1x", 76, "1x", "ipad", "ios"),
    IconSpec("ipad-76@2x", 152, "2x", "ipad", "ios"),
    IconSpec("ipad-83.5@2x", 167, "2x", "ipad", "ios"),
    IconSpec("appstore-1024", 1024, "1x", "ios-marketing", "ios"),
]

ANDROID_ICONS: List[IconSpec] = [
    IconSpec("mipmap-mdpi", 48, "1x", "android", "android"),
    IconSpec("mipmap-hdpi", 72, "1x", "android", "android"),
    IconSpec("mipmap-xhdpi", 96, "1x", "android", "android"),
    IconSpec("mipmap-xxhdpi", 144, "1x", "android", "android"),
    IconSpec("mipmap-xxxhdpi", 192, "1x", "android", "android"),
    IconSpec("playstore-512", 512, "1x", "android", "android"),
]

WEB_ICONS: List[IconSpec] = [
    IconSpec("favicon-16", 16, "1x", "web", "web"),
    IconSpec("favicon-32", 32, "1x", "web", "web"),
    IconSpec("apple-touch-icon", 180, "1x", "web", "web"),
    IconSpec("icon-192", 192, "1x", "web", "web"),
    IconSpec("icon-512", 512, "1x", "web", "web"),
]


# ── Icon Generator ────────────────────────────────────────────────────────

class IconGenerator:
    """Generate icons using ffmpeg scaling."""

    @staticmethod
    def check_ffmpeg() -> bool:
        try:
            r = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
            return r.returncode == 0
        except FileNotFoundError:
            return False

    @staticmethod
    def resize(source: str, output: str, size: int) -> Dict:
        """Resize image to exact square dimensions."""
        os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
        try:
            r = subprocess.run(
                ["ffmpeg", "-i", source, "-y",
                 "-vf", f"scale={size}:{size}:flags=lanczos",
                 output],
                capture_output=True, text=True, timeout=30,
            )
            if os.path.isfile(output):
                return {"generated": output, "size": size, "bytes": os.path.getsize(output)}
            return {"error": r.stderr[-256:]}
        except FileNotFoundError:
            return {"error": "ffmpeg not found"}
        except Exception as e:
            return {"error": str(e)[:256]}

    @staticmethod
    def generate_set(source: str, output_dir: str,
                      specs: List[IconSpec]) -> Dict:
        """Generate a full set of icons from one source."""
        results = {"generated": 0, "failed": 0, "icons": []}
        for spec in specs:
            out_path = os.path.join(output_dir, spec.platform, f"{spec.name}.png")
            r = IconGenerator.resize(source, out_path, spec.size)
            if "generated" in r:
                results["generated"] += 1
                results["icons"].append({"name": spec.name, "size": spec.size})
            else:
                results["failed"] += 1
        return results


# ── Asset Catalog Generator ──────────────────────────────────────────────

class AssetCatalogGenerator:
    """Generate Xcode-compatible Contents.json files."""

    @staticmethod
    def generate_ios_contents(output_dir: str) -> Dict:
        """Generate Contents.json for iOS AppIcon set."""
        images = []
        for spec in IOS_ICONS:
            pt_size = spec.size / int(spec.scale[0])
            images.append({
                "filename": f"{spec.name}.png",
                "idiom": spec.idiom,
                "scale": spec.scale,
                "size": f"{pt_size}x{pt_size}",
            })
        contents = {"images": images, "info": {"author": "omni-appicon", "version": 1}}
        ios_dir = os.path.join(output_dir, "ios")
        os.makedirs(ios_dir, exist_ok=True)
        path = os.path.join(ios_dir, "Contents.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(contents, f, indent=2)
        return {"generated": path, "icons": len(images)}

    @staticmethod
    def generate_android_manifest(output_dir: str) -> Dict:
        """Generate icon reference manifest for Android."""
        entries = []
        for spec in ANDROID_ICONS:
            entries.append({"directory": spec.name, "size": spec.size, "file": "ic_launcher.png"})
        android_dir = os.path.join(output_dir, "android")
        os.makedirs(android_dir, exist_ok=True)
        path = os.path.join(android_dir, "icon_manifest.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"icons": entries, "adaptive_icon": True}, f, indent=2)
        return {"generated": path, "entries": len(entries)}


# ── Source Image Validator ────────────────────────────────────────────────

class SourceValidator:
    """Validate source image for icon generation."""

    @staticmethod
    def validate(source: str) -> Dict:
        if not os.path.isfile(source):
            return {"valid": False, "error": "File not found"}
        size_kb = round(os.path.getsize(source) / 1024, 2)
        ext = os.path.splitext(source)[1].lower()
        valid_exts = {".png", ".jpg", ".jpeg", ".svg", ".webp"}

        # Get dimensions via ffprobe
        width = height = 0
        try:
            r = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json",
                 "-show_streams", source],
                capture_output=True, text=True, timeout=10,
            )
            if r.returncode == 0:
                data = json.loads(r.stdout)
                for s in data.get("streams", []):
                    if s.get("codec_type") == "video":
                        width = s.get("width", 0)
                        height = s.get("height", 0)
                        break
        except Exception:
            pass

        is_square = width == height and width > 0
        min_size_ok = width >= 1024 and height >= 1024

        return {
            "valid": ext in valid_exts and is_square and min_size_ok,
            "width": width, "height": height,
            "is_square": is_square,
            "min_1024": min_size_ok,
            "format": ext.lstrip("."),
            "size_kb": size_kb,
            "recommendations": [] if (is_square and min_size_ok) else
                ["Use a 1024x1024 PNG for best results"] if not min_size_ok else
                ["Source should be square (equal width/height)"],
        }


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniAppIconEngine:
    """
    OMNI AppIcon Engine — Zero-Mock App Icon Generation Pipeline.

    Capabilities (all native subprocess + json):
      - Source image validation (dimensions, format)
      - iOS icon set generation (18 sizes)
      - Android icon set generation (6 sizes)
      - Web favicon set generation (5 sizes)
      - Xcode Contents.json generation
      - Android manifest generation
    """

    def __init__(self):
        self.generator = IconGenerator()
        self.catalog = AssetCatalogGenerator()
        self.validator = SourceValidator()

    def validate_source(self, path: str) -> Dict:
        return self.validator.validate(path)

    def generate_all(self, source: str, output_dir: str) -> Dict:
        """Generate all platform icons from one source."""
        validation = self.validator.validate(source)
        all_specs = IOS_ICONS + ANDROID_ICONS + WEB_ICONS
        gen = self.generator.generate_set(source, output_dir, all_specs)
        self.catalog.generate_ios_contents(output_dir)
        self.catalog.generate_android_manifest(output_dir)
        return {
            "source_valid": validation.get("valid", False),
            "total_icons": gen["generated"],
            "failed": gen["failed"],
            "platforms": {"ios": len(IOS_ICONS), "android": len(ANDROID_ICONS), "web": len(WEB_ICONS)},
        }

    def diagnostics(self) -> Dict:
        return {
            "engine": "OmniAppIconEngine",
            "status": "active",
            "ffmpeg": self.generator.check_ffmpeg(),
            "icon_specs": {
                "ios": len(IOS_ICONS),
                "android": len(ANDROID_ICONS),
                "web": len(WEB_ICONS),
                "total": len(IOS_ICONS) + len(ANDROID_ICONS) + len(WEB_ICONS),
            },
            "capabilities": ["source_validate", "ios_iconset", "android_iconset",
                             "web_favicons", "contents_json", "android_manifest"],
        }


if __name__ == "__main__":
    engine = OmniAppIconEngine()
    print(json.dumps(engine.diagnostics(), indent=2))
