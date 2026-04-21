ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI GRADLE PLAY PUBLISHER ENGINE — Android Google Play Automated Publisher
# ===========================================================================
# Source Paradigm: https://github.com/Triple-T/gradle-play-publisher
# Domain Layer  : Mobile
# Zero-Mock     : 100% Native — subprocess, os, json, real file operations
# ===========================================================================
"""
Gradle Play Publisher (GPP) teaches us:
  1. Automated APK/AAB upload to Google Play Console
  2. Store listing management (title, description, screenshots)
  3. Release track management (internal, alpha, beta, production)
  4. Version code auto-increment
  5. Gradle task integration for CI/CD publishing
  6. Service account authentication for Play Developer API

This engine distills those paradigms into OMNI-native Python automation
for Android app publishing lifecycle management.
"""

import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


# ── Data Models ──────────────────────────────────────────────────────────────

class ReleaseTrack(Enum):
    INTERNAL = "internal"
    ALPHA = "alpha"
    BETA = "beta"
    PRODUCTION = "production"


class ReleaseStatus(Enum):
    DRAFT = "draft"
    IN_PROGRESS = "inProgress"
    HALTED = "halted"
    COMPLETED = "completed"


@dataclass
class StoreListing:
    language: str = "en-US"
    title: str = ""
    short_description: str = ""
    full_description: str = ""
    video_url: str = ""
    screenshots_dir: str = ""      # path to screenshots folder


@dataclass
class ReleaseConfig:
    track: ReleaseTrack = ReleaseTrack.INTERNAL
    status: ReleaseStatus = ReleaseStatus.COMPLETED
    release_name: str = ""
    release_notes: Dict[str, str] = field(default_factory=dict)  # lang -> notes
    user_fraction: float = 1.0     # staged rollout (0.0 - 1.0)
    version_code: int = 0
    version_name: str = ""


@dataclass
class AppBundle:
    path: str                       # path to .aab or .apk file
    package_name: str
    version_code: int
    version_name: str
    size_bytes: int = 0
    sha256: str = ""


# ── Gradle Integration ──────────────────────────────────────────────────────

class GradleRunner:
    """Execute Gradle tasks natively via subprocess."""

    @staticmethod
    def find_gradle_wrapper(project_dir: str) -> Optional[str]:
        """Find gradlew/gradlew.bat in a project directory."""
        if os.name == "nt":
            wrapper = os.path.join(project_dir, "gradlew.bat")
        else:
            wrapper = os.path.join(project_dir, "gradlew")
        return wrapper if os.path.isfile(wrapper) else None

    @staticmethod
    def run_task(project_dir: str, task: str, extra_args: List[str] = None) -> Dict:
        """Execute a Gradle task in the project directory."""
        wrapper = GradleRunner.find_gradle_wrapper(project_dir)
        if not wrapper:
            # Fallback to system gradle
            wrapper = "gradle"

        cmd = [wrapper, task] + (extra_args or [])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True, text=True,
                cwd=project_dir,
                timeout=600,  # 10 min for builds
            )
            return {
                "status": "success" if result.returncode == 0 else "error",
                "task": task,
                "exit_code": result.returncode,
                "stdout": result.stdout[:8192],
                "stderr": result.stderr[:4096],
            }
        except FileNotFoundError:
            return {"status": "error", "message": f"Gradle not found: {wrapper}"}
        except subprocess.TimeoutExpired:
            return {"status": "error", "message": "Build timed out (600s)"}
        except Exception as e:
            return {"status": "error", "message": str(e)[:256]}


# ── Version Manager ─────────────────────────────────────────────────────────

class VersionManager:
    """Manage Android version codes and names from build.gradle."""

    @staticmethod
    def read_version(project_dir: str) -> Dict:
        """Parse versionCode and versionName from build.gradle(.kts)."""
        for fname in ["app/build.gradle.kts", "app/build.gradle"]:
            gradle_path = os.path.join(project_dir, fname)
            if os.path.isfile(gradle_path):
                with open(gradle_path, "r", encoding="utf-8") as f:
                    content = f.read()

                version_code = 0
                version_name = ""

                for line in content.splitlines():
                    stripped = line.strip()
                    if "versionCode" in stripped:
                        # Extract number
                        parts = stripped.split("=") if "=" in stripped else stripped.split()
                        for part in reversed(parts):
                            clean = part.strip().rstrip(",").strip('"').strip("'")
                            if clean.isdigit():
                                version_code = int(clean)
                                break

                    if "versionName" in stripped:
                        parts = stripped.split("=") if "=" in stripped else stripped.split()
                        for part in reversed(parts):
                            clean = part.strip().rstrip(",").strip('"').strip("'")
                            if clean and clean[0].isdigit():
                                version_name = clean
                                break

                return {
                    "file": gradle_path,
                    "version_code": version_code,
                    "version_name": version_name,
                }
        return {"error": "build.gradle not found"}

    @staticmethod
    def bump_version_code(project_dir: str) -> Dict:
        """Increment versionCode by 1 in build.gradle."""
        current = VersionManager.read_version(project_dir)
        if "error" in current:
            return current

        gradle_path = current["file"]
        old_code = current["version_code"]
        new_code = old_code + 1

        with open(gradle_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace versionCode line
        new_content = content.replace(
            f"versionCode {old_code}", f"versionCode {new_code}"
        ).replace(
            f"versionCode = {old_code}", f"versionCode = {new_code}"
        )

        if new_content != content:
            with open(gradle_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return {"status": "success", "old_code": old_code, "new_code": new_code}
        return {"status": "no_change", "version_code": old_code}


# ── Bundle Locator ──────────────────────────────────────────────────────────

class BundleLocator:
    """Find built APK/AAB files in build output directories."""

    @staticmethod
    def find_bundles(project_dir: str) -> List[AppBundle]:
        """Locate .aab and .apk files in the build outputs."""
        bundles = []
        build_dirs = [
            os.path.join(project_dir, "app", "build", "outputs", "bundle"),
            os.path.join(project_dir, "app", "build", "outputs", "apk"),
        ]

        for build_dir in build_dirs:
            if not os.path.isdir(build_dir):
                continue
            for root, dirs, files in os.walk(build_dir):
                for f in files:
                    if f.endswith((".aab", ".apk")):
                        full = os.path.join(root, f)
                        import hashlib
                        sha = hashlib.sha256(open(full, "rb").read()).hexdigest()
                        bundles.append(AppBundle(
                            path=full,
                            package_name="",  # would parse from manifest
                            version_code=0,
                            version_name="",
                            size_bytes=os.path.getsize(full),
                            sha256=sha,
                        ))
        return bundles


# ── Store Listing Manager ──────────────────────────────────────────────────

class StoreListingManager:
    """Manage Play Store listing metadata files (GPP format)."""

    @staticmethod
    def write_listing(project_dir: str, listing: StoreListing) -> Dict:
        """Write store listing files in the GPP directory structure."""
        listing_dir = os.path.join(
            project_dir, "app", "src", "main", "play",
            "listings", listing.language,
        )
        os.makedirs(listing_dir, exist_ok=True)

        files_written = []

        if listing.title:
            path = os.path.join(listing_dir, "title.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write(listing.title)
            files_written.append(path)

        if listing.short_description:
            path = os.path.join(listing_dir, "short-description.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write(listing.short_description)
            files_written.append(path)

        if listing.full_description:
            path = os.path.join(listing_dir, "full-description.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write(listing.full_description)
            files_written.append(path)

        return {"status": "success", "files_written": files_written, "language": listing.language}

    @staticmethod
    def read_listing(project_dir: str, language: str = "en-US") -> StoreListing:
        """Read existing store listing files."""
        listing_dir = os.path.join(
            project_dir, "app", "src", "main", "play", "listings", language,
        )
        listing = StoreListing(language=language)

        for field_name, filename in [
            ("title", "title.txt"),
            ("short_description", "short-description.txt"),
            ("full_description", "full-description.txt"),
        ]:
            path = os.path.join(listing_dir, filename)
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8") as f:
                    setattr(listing, field_name, f.read().strip())

        return listing


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniGradlePlayPublisherEngine:
    """
    OMNI Gradle Play Publisher Engine — Zero-Mock Android Publishing Automation.

    Capabilities (all native stdlib):
      - Gradle task execution (assembleRelease, bundleRelease)
      - Version code auto-increment
      - AAB/APK bundle discovery with SHA256
      - Store listing file management (GPP format)
      - Release track configuration
    """

    def __init__(self):
        self.gradle = GradleRunner()
        self.version_mgr = VersionManager()
        self.bundle_locator = BundleLocator()
        self.listing_mgr = StoreListingManager()

    def build_release(self, project_dir: str, bundle_type: str = "aab") -> Dict:
        """Build a release AAB or APK."""
        task = "bundleRelease" if bundle_type == "aab" else "assembleRelease"
        return self.gradle.run_task(project_dir, task)

    def publish_pipeline(self, project_dir: str,
                          track: ReleaseTrack = ReleaseTrack.INTERNAL,
                          auto_bump: bool = True) -> Dict:
        """Full publish pipeline: bump → build → locate → report."""
        results = {"pipeline": "publish", "steps": []}

        # Step 1: Version bump
        if auto_bump:
            bump = self.version_mgr.bump_version_code(project_dir)
            results["steps"].append({"step": "version_bump", "result": bump})

        # Step 2: Build
        build = self.build_release(project_dir)
        results["steps"].append({"step": "build", "result": build})

        if build.get("status") != "success":
            results["status"] = "failed_at_build"
            return results

        # Step 3: Locate bundles
        bundles = self.bundle_locator.find_bundles(project_dir)
        results["steps"].append({
            "step": "locate_bundles",
            "bundles_found": len(bundles),
            "bundles": [{"path": b.path, "size": b.size_bytes, "sha256": b.sha256} for b in bundles],
        })

        # Step 4: Report readiness
        results["status"] = "ready_for_upload"
        results["target_track"] = track.value
        results["version"] = self.version_mgr.read_version(project_dir)

        return results

    def diagnostics(self) -> Dict:
        return {
            "engine": "OmniGradlePlayPublisherEngine",
            "status": "active",
            "capabilities": ["gradle_build", "version_bump", "bundle_locate",
                             "store_listing", "release_track_config"],
        }


if __name__ == "__main__":
    engine = OmniGradlePlayPublisherEngine()
    print("[GPP] Diagnostics:")
    print(json.dumps(engine.diagnostics(), indent=2))
