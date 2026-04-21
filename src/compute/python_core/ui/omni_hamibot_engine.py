ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI HAMIBOT ENGINE — Android Device Automation & Scripting
# ===========================================================================
# Source Paradigm: https://github.com/hamibot/hamibot
# Domain Layer  : Mobile (Android Automation)
# Zero-Mock     : 100% Native — subprocess (ADB), json, os, socket
# ===========================================================================
"""
Hamibot teaches us:
  1. JavaScript-based Android automation (Auto.js paradigm)
  2. Accessibility Service interaction for UI control
  3. Screen tap/swipe/scroll simulation via ADB
  4. Package management (install, uninstall, launch)
  5. Device info extraction (model, battery, storage)
  6. Script deployment to Android devices

This engine distills those paradigms into OMNI-native Python for
Android device control using ADB subprocess commands exclusively.
"""

import json
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ── Data Models ──────────────────────────────────────────────────────────────

@dataclass
class AndroidDevice:
    serial: str
    model: str = ""
    manufacturer: str = ""
    android_version: str = ""
    sdk_version: int = 0
    resolution: str = ""
    battery_level: int = -1
    battery_status: str = ""
    storage_total_gb: float = 0
    storage_free_gb: float = 0
    is_online: bool = False


@dataclass
class AppInfo:
    package: str
    version_name: str = ""
    version_code: int = 0
    install_time: str = ""
    is_system: bool = False


# ── ADB Bridge ─────────────────────────────────────────────────────────────

class ADBBridge:
    """Native ADB subprocess interface for Android device control."""

    @staticmethod
    def check_adb() -> Dict:
        """Check if ADB is installed and accessible."""
        try:
            r = subprocess.run(["adb", "version"], capture_output=True, text=True, timeout=5)
            version = r.stdout.strip().split("\n")[0] if r.returncode == 0 else ""
            return {"installed": r.returncode == 0, "version": version}
        except FileNotFoundError:
            return {"installed": False, "version": ""}

    @staticmethod
    def devices() -> List[Dict]:
        """List connected Android devices."""
        try:
            r = subprocess.run(["adb", "devices", "-l"], capture_output=True, text=True, timeout=5)
            devices = []
            for line in r.stdout.strip().split("\n")[1:]:
                if "\t" in line or "device" in line:
                    parts = line.split()
                    if len(parts) >= 2 and parts[1] in ("device", "online"):
                        serial = parts[0]
                        model = ""
                        for p in parts[2:]:
                            if p.startswith("model:"):
                                model = p.split(":")[1]
                        devices.append({"serial": serial, "status": parts[1], "model": model})
            return devices
        except FileNotFoundError:
            return []

    @staticmethod
    def shell(serial: str, command: str, timeout: int = 10) -> Dict:
        """Execute an ADB shell command on a device."""
        try:
            r = subprocess.run(
                ["adb", "-s", serial, "shell", command],
                capture_output=True, text=True, timeout=timeout,
            )
            return {
                "exit_code": r.returncode,
                "stdout": r.stdout.strip()[:4096],
                "stderr": r.stderr.strip()[:2048],
            }
        except FileNotFoundError:
            return {"error": "adb not found"}
        except subprocess.TimeoutExpired:
            return {"error": f"Timeout ({timeout}s)"}
        except Exception as e:
            return {"error": str(e)[:256]}

    @staticmethod
    def get_prop(serial: str, prop: str) -> str:
        """Get a device property via getprop."""
        result = ADBBridge.shell(serial, f"getprop {prop}")
        return result.get("stdout", "").strip()


# ── Device Inspector ───────────────────────────────────────────────────────

class DeviceInspector:
    """Extract detailed device information via ADB."""

    @staticmethod
    def inspect(serial: str) -> AndroidDevice:
        """Get full device info."""
        device = AndroidDevice(serial=serial, is_online=True)

        device.model = ADBBridge.get_prop(serial, "ro.product.model")
        device.manufacturer = ADBBridge.get_prop(serial, "ro.product.manufacturer")
        device.android_version = ADBBridge.get_prop(serial, "ro.build.version.release")

        sdk = ADBBridge.get_prop(serial, "ro.build.version.sdk")
        device.sdk_version = int(sdk) if sdk.isdigit() else 0

        # Resolution
        wm = ADBBridge.shell(serial, "wm size")
        res_match = re.search(r'(\d+x\d+)', wm.get("stdout", ""))
        device.resolution = res_match.group(1) if res_match else ""

        # Battery
        battery = ADBBridge.shell(serial, "dumpsys battery")
        bat_out = battery.get("stdout", "")
        level_match = re.search(r'level:\s*(\d+)', bat_out)
        status_match = re.search(r'status:\s*(\d+)', bat_out)
        device.battery_level = int(level_match.group(1)) if level_match else -1
        status_map = {"2": "charging", "3": "discharging", "4": "not_charging", "5": "full"}
        device.battery_status = status_map.get(
            status_match.group(1) if status_match else "", "unknown"
        )

        # Storage
        storage = ADBBridge.shell(serial, "df /data")
        storage_out = storage.get("stdout", "")
        for line in storage_out.split("\n"):
            if "/data" in line:
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        total = int(parts[1]) / (1024 * 1024)  # KB → GB
                        free = int(parts[3]) / (1024 * 1024)
                        device.storage_total_gb = round(total, 2)
                        device.storage_free_gb = round(free, 2)
                    except (ValueError, IndexError):
                        pass

        return device


# ── UI Automator ───────────────────────────────────────────────────────────

class UIAutomator:
    """Simulate user interactions on Android via ADB."""

    @staticmethod
    def tap(serial: str, x: int, y: int) -> Dict:
        return ADBBridge.shell(serial, f"input tap {x} {y}")

    @staticmethod
    def swipe(serial: str, x1: int, y1: int, x2: int, y2: int,
              duration_ms: int = 300) -> Dict:
        return ADBBridge.shell(serial, f"input swipe {x1} {y1} {x2} {y2} {duration_ms}")

    @staticmethod
    def type_text(serial: str, text: str) -> Dict:
        safe_text = text.replace(" ", "%s").replace("'", "\\'")
        return ADBBridge.shell(serial, f"input text '{safe_text}'")

    @staticmethod
    def key_event(serial: str, keycode: str) -> Dict:
        """Send a key event (HOME, BACK, POWER, etc.)."""
        return ADBBridge.shell(serial, f"input keyevent {keycode}")

    @staticmethod
    def screenshot(serial: str, local_path: str) -> Dict:
        """Take a screenshot and pull it to local."""
        remote = "/sdcard/omni_screenshot.png"
        ADBBridge.shell(serial, f"screencap -p {remote}")
        try:
            r = subprocess.run(
                ["adb", "-s", serial, "pull", remote, local_path],
                capture_output=True, text=True, timeout=10,
            )
            return {
                "status": "success" if r.returncode == 0 else "error",
                "path": local_path if r.returncode == 0 else "",
            }
        except Exception as e:
            return {"status": "error", "error": str(e)[:256]}


# ── Package Manager ────────────────────────────────────────────────────────

class PackageManager:
    """Manage Android packages via ADB."""

    @staticmethod
    def list_packages(serial: str, third_party: bool = True) -> List[str]:
        flag = "-3" if third_party else ""
        result = ADBBridge.shell(serial, f"pm list packages {flag}")
        packages = []
        for line in result.get("stdout", "").split("\n"):
            if line.startswith("package:"):
                packages.append(line[8:].strip())
        return packages

    @staticmethod
    def launch_app(serial: str, package: str) -> Dict:
        return ADBBridge.shell(serial, f"monkey -p {package} -c android.intent.category.LAUNCHER 1")

    @staticmethod
    def force_stop(serial: str, package: str) -> Dict:
        return ADBBridge.shell(serial, f"am force-stop {package}")

    @staticmethod
    def install_apk(serial: str, apk_path: str) -> Dict:
        try:
            r = subprocess.run(
                ["adb", "-s", serial, "install", "-r", apk_path],
                capture_output=True, text=True, timeout=120,
            )
            return {
                "status": "success" if r.returncode == 0 else "error",
                "output": r.stdout[:512],
            }
        except Exception as e:
            return {"status": "error", "error": str(e)[:256]}


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniHamibotEngine:
    """
    OMNI Hamibot Engine — Zero-Mock Android Device Automation.

    Capabilities (all native ADB subprocess):
      - Device discovery and inspection
      - UI automation (tap, swipe, type, key events)
      - Screenshot capture
      - Package management (list, install, launch, stop)
      - Battery and storage monitoring
    """

    def __init__(self):
        self.adb = ADBBridge()
        self.inspector = DeviceInspector()
        self.ui = UIAutomator()
        self.packages = PackageManager()

    def list_devices(self) -> List[Dict]:
        return self.adb.devices()

    def inspect_device(self, serial: str) -> Dict:
        d = self.inspector.inspect(serial)
        return {
            "serial": d.serial, "model": d.model,
            "manufacturer": d.manufacturer,
            "android": d.android_version, "sdk": d.sdk_version,
            "resolution": d.resolution,
            "battery": {"level": d.battery_level, "status": d.battery_status},
            "storage_gb": {"total": d.storage_total_gb, "free": d.storage_free_gb},
        }

    def diagnostics(self) -> Dict:
        adb = self.adb.check_adb()
        devices = self.adb.devices()
        return {
            "engine": "OmniHamibotEngine",
            "status": "active",
            "adb": adb,
            "connected_devices": len(devices),
            "devices": devices,
            "capabilities": ["device_discovery", "device_inspect", "ui_tap",
                             "ui_swipe", "ui_type", "screenshot", "package_mgmt",
                             "battery_monitor", "storage_monitor"],
        }


if __name__ == "__main__":
    engine = OmniHamibotEngine()
    print(json.dumps(engine.diagnostics(), indent=2))
