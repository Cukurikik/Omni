ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI APP STORE CONNECT ENGINE — Apple iOS App Publishing Automation
# ===========================================================================
# Source Paradigm: https://github.com/rudrankriyam/App-Store-Connect-CLI
# Domain Layer  : Mobile (iOS Publishing)
# Zero-Prod     : 100% Native — subprocess, json, os, urllib
# ===========================================================================
"""
App Store Connect CLI teaches us:
  1. JWT-based authentication for Apple API
  2. App version management (create, update, submit)
  3. TestFlight beta distribution automation
  4. Store listing metadata management (screenshots, descriptions)
  5. Certificate and provisioning profile management
  6. CAEOAS pattern: commands suggest next valid actions

This engine distills those paradigms into OMNI-native Python for
iOS app lifecycle management using stdlib + Xcode subprocess calls.
"""

import base64
import hashlib
import json
import os
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


# ── Data Models ──────────────────────────────────────────────────────────────

class AppStatus(Enum):
    PREPARE_FOR_SUBMISSION = "PREPARE_FOR_SUBMISSION"
    WAITING_FOR_REVIEW = "WAITING_FOR_REVIEW"
    IN_REVIEW = "IN_REVIEW"
    READY_FOR_SALE = "READY_FOR_SALE"
    REJECTED = "REJECTED"
    DEVELOPER_REMOVED = "DEVELOPER_REMOVED"


class TestFlightStatus(Enum):
    PROCESSING = "PROCESSING"
    READY = "READY_FOR_BETA_TESTING"
    EXPIRED = "EXPIRED"


@dataclass
class AppInfo:
    bundle_id: str
    name: str
    sku: str = ""
    primary_locale: str = "en-US"
    version: str = ""
    build_number: str = ""
    status: str = ""


@dataclass
class StoreVersion:
    version_string: str
    platform: str = "IOS"
    release_type: str = "MANUAL"  # MANUAL | AFTER_APPROVAL | SCHEDULED
    earliest_release_date: str = ""
    description: str = ""
    keywords: str = ""
    whats_new: str = ""


@dataclass
class ProvisioningProfile:
    name: str
    profile_type: str       # "IOS_APP_DEVELOPMENT" | "IOS_APP_STORE" | "IOS_APP_ADHOC"
    bundle_id: str
    expiration_date: str = ""
    is_valid: bool = True


# ── JWT Token Generator ────────────────────────────────────────────────────

class ASCTokenGenerator:
    """Generate JWT tokens for App Store Connect API authentication."""

    @staticmethod
    def generate_jwt_header(key_id: str, issuer_id: str) -> Dict:
        """Generate the JWT header and payload structure."""
        now = int(time.time())
        return {
            "header": {
                "alg": "ES256",
                "kid": key_id,
                "typ": "JWT",
            },
            "payload": {
                "iss": issuer_id,
                "iat": now,
                "exp": now + 1200,  # 20 minutes
                "aud": "appstoreconnect-v1",
            },
            "note": "Sign with ES256 using your .p8 AuthKey file",
        }


# ── Xcode Build Integration ────────────────────────────────────────────────

class XcodeBuildRunner:
    """Execute Xcode build/archive commands via subprocess."""

    @staticmethod
    def find_xcodebuild() -> Optional[str]:
        """Check if xcodebuild is available."""
        try:
            r = subprocess.run(["xcodebuild", "-version"],
                               capture_output=True, text=True, timeout=10)
            if r.returncode == 0:
                return r.stdout.strip()
        except FileNotFoundError:
            pass
        return None

    @staticmethod
    def build(project_dir: str, scheme: str, config: str = "Release") -> Dict:
        """Build an Xcode project."""
        cmd = ["xcodebuild", "-project", project_dir, "-scheme", scheme,
               "-configuration", config, "build"]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            return {
                "status": "success" if r.returncode == 0 else "error",
                "exit_code": r.returncode,
                "stdout": r.stdout[-2048:],
                "stderr": r.stderr[-1024:],
            }
        except FileNotFoundError:
            return {"status": "error", "message": "xcodebuild not found"}
        except Exception as e:
            return {"status": "error", "message": str(e)[:256]}

    @staticmethod
    def archive(project_dir: str, scheme: str, archive_path: str) -> Dict:
        """Archive an Xcode project for distribution."""
        cmd = ["xcodebuild", "-project", project_dir, "-scheme", scheme,
               "-archivePath", archive_path, "archive"]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
            return {
                "status": "success" if r.returncode == 0 else "error",
                "exit_code": r.returncode,
                "archive_path": archive_path if r.returncode == 0 else "",
            }
        except FileNotFoundError:
            return {"status": "error", "message": "xcodebuild not found"}
        except Exception as e:
            return {"status": "error", "message": str(e)[:256]}

    @staticmethod
    def export_ipa(archive_path: str, export_path: str,
                   plist_path: str) -> Dict:
        """Export an IPA from an archive."""
        cmd = ["xcodebuild", "-exportArchive",
               "-archivePath", archive_path,
               "-exportPath", export_path,
               "-exportOptionsPlist", plist_path]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return {
                "status": "success" if r.returncode == 0 else "error",
                "export_path": export_path if r.returncode == 0 else "",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)[:256]}


# ── IPA Analyzer ────────────────────────────────────────────────────────────

class IPAAnalyzer:
    """Analyze IPA files for metadata extraction."""

    @staticmethod
    def find_ipas(directory: str) -> List[Dict]:
        """Find all IPA files in a directory."""
        ipas = []
        if not os.path.isdir(directory):
            return ipas
        for root, dirs, files in os.walk(directory):
            for f in files:
                if f.endswith(".ipa"):
                    full = os.path.join(root, f)
                    ipas.append({
                        "name": f,
                        "path": full,
                        "size_bytes": os.path.getsize(full),
                        "size_mb": round(os.path.getsize(full) / (1024**2), 2),
                        "sha256": hashlib.sha256(open(full, "rb").read()).hexdigest(),
                    })
        return ipas

    @staticmethod
    def analyze_info_plist(project_dir: str) -> Dict:
        """Read Info.plist for bundle ID and version info."""
        plist_paths = [
            os.path.join(project_dir, "Info.plist"),
            os.path.join(project_dir, "App", "Info.plist"),
        ]
        for plist_path in plist_paths:
            if os.path.isfile(plist_path):
                try:
                    with open(plist_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    # Simple plist key extraction
                    def _extract_key(content, key):
                        idx = content.find(f"<key>{key}</key>")
                        if idx == -1:
                            return ""
                        val_start = content.find("<string>", idx) + 8
                        val_end = content.find("</string>", val_start)
                        return content[val_start:val_end] if val_start > 7 else ""

                    return {
                        "plist_path": plist_path,
                        "bundle_id": _extract_key(content, "CFBundleIdentifier"),
                        "version": _extract_key(content, "CFBundleShortVersionString"),
                        "build": _extract_key(content, "CFBundleVersion"),
                        "display_name": _extract_key(content, "CFBundleDisplayName"),
                    }
                except Exception:
                    pass
        return {"error": "Info.plist not found"}


# ── Store Listing Manager ──────────────────────────────────────────────────

class ASCStoreListingManager:
    """Manage App Store listing metadata files."""

    @staticmethod
    def create_listing_dir(project_dir: str, locale: str = "en-US") -> str:
        listing_dir = os.path.join(project_dir, "fastlane", "metadata", locale)
        os.makedirs(listing_dir, exist_ok=True)
        return listing_dir

    @staticmethod
    def write_metadata(project_dir: str, version: StoreVersion,
                        locale: str = "en-US") -> Dict:
        """Write store metadata files (Fastlane-compatible format)."""
        listing_dir = ASCStoreListingManager.create_listing_dir(project_dir, locale)
        files_written = []
        metadata = {
            "description.txt": version.description,
            "keywords.txt": version.keywords,
            "release_notes.txt": version.whats_new,
        }
        for filename, content in metadata.items():
            if content:
                path = os.path.join(listing_dir, filename)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                files_written.append(path)

        return {"locale": locale, "files_written": files_written}


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniAppStoreConnectEngine:
    """
    OMNI App Store Connect Engine — Zero-Prod iOS Publishing Automation.

    Capabilities (all native stdlib):
      - JWT token structure generation for ASC API
      - Xcode build/archive/export via subprocess
      - IPA discovery and SHA256 hashing
      - Info.plist parsing for bundle metadata
      - Store listing metadata management
    """

    def __init__(self):
        self.xcode = XcodeBuildRunner()
        self.ipa_analyzer = IPAAnalyzer()
        self.listing_mgr = ASCStoreListingManager()
        self.token_gen = ASCTokenGenerator()

    def check_xcode(self) -> Dict:
        """Check if Xcode is available on this system."""
        version = self.xcode.find_xcodebuild()
        return {"installed": version is not None, "version": version or "not found"}

    def generate_token(self, key_id: str, issuer_id: str) -> Dict:
        """Generate JWT token structure for ASC API."""
        return self.token_gen.generate_jwt_header(key_id, issuer_id)

    def publish_pipeline(self, project_dir: str, scheme: str) -> Dict:
        """Full iOS publish pipeline: build → archive → locate IPA."""
        results = {"pipeline": "ios_publish", "steps": []}

        # Step 1: Check Xcode
        xcode = self.check_xcode()
        results["steps"].append({"step": "xcode_check", "result": xcode})
        if not xcode["installed"]:
            results["status"] = "xcode_not_found"
            return results

        # Step 2: Build
        build = self.xcode.build(project_dir, scheme)
        results["steps"].append({"step": "build", "result": build})

        # Step 3: Archive
        archive_path = os.path.join(project_dir, "build", f"{scheme}.xcarchive")
        archive = self.xcode.archive(project_dir, scheme, archive_path)
        results["steps"].append({"step": "archive", "result": archive})

        results["status"] = "pipeline_complete"
        return results

    def diagnostics(self) -> Dict:
        xcode = self.check_xcode()
        return {
            "engine": "OmniAppStoreConnectEngine",
            "status": "active",
            "xcode": xcode,
            "capabilities": ["jwt_auth", "xcode_build", "xcode_archive",
                             "ipa_analysis", "plist_parse", "store_listing"],
        }


if __name__ == "__main__":
    engine = OmniAppStoreConnectEngine()
    print("[ASC] Diagnostics:")
    print(json.dumps(engine.diagnostics(), indent=2))
