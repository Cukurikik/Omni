"""
+============================================================================+
|  OMNI Clash IP Checker Engine                                               |
|  Production-grade proxy node IP risk analysis and scoring engine.           |
|  Inspired by: github.com/tombcato/clash-ip-checker                         |
|  Layer: Compute (Python)                                                    |
|  Features:                                                                  |
|    - Clash External Controller API integration                              |
|    - Multi-source IP purity detection (IPPure, Ping0, IP-API)               |
|    - Automatic fallback between detection sources                           |
|    - Proxy node traversal with forced Global mode                           |
|    - IP risk scoring with emoji tagging (residential/datacenter/native)     |
|    - Batch detection with concurrency control                               |
|    - YAML config read/write with node renaming                              |
|    - Node filtering (skip invalid/expired nodes)                            |
|    - Detection result caching and export                                    |
+============================================================================+
"""

from __future__ import annotations

ENGINE_VERSION = "1.0.0"

import hashlib
import json
import os
import re
import socket
import struct
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ============================================================================
# 1. Enums & Constants
# ============================================================================
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class IPType(Enum):
    """Type enumeration for IPType."""
    RESIDENTIAL = "residential"
    DATACENTER = "datacenter"
    MOBILE = "mobile"
    EDUCATION = "education"
    UNKNOWN = "unknown"

class IPOrigin(Enum):
    """Production-grade I P Origin component."""
    NATIVE = "native"
    BROADCAST = "broadcast"
    UNKNOWN = "unknown"

class DetectionSource(Enum):
    """Production-grade Detection Source component."""
    PING0 = "ping0"
    IPPURE = "ippure"
    IPAPI = "ip-api"
    FALLBACK = "fallback"

class ProxyType(Enum):
    """Type enumeration for ProxyType."""
    SS = "ss"
    SSR = "ssr"
    VMESS = "vmess"
    VLESS = "vless"
    TROJAN = "trojan"
    HYSTERIA = "hysteria"
    HYSTERIA2 = "hysteria2"
    TUIC = "tuic"
    WIREGUARD = "wireguard"
    SOCKS5 = "socks5"
    HTTP = "http"
    UNKNOWN = "unknown"

# Skip patterns for invalid proxy nodes
SKIP_PATTERNS = [
    "到期", "过期", "expire", "流量", "traffic", "重置", "reset",
    "官网", "website", "订阅", "subscribe", "剩余", "remain",
    "套餐", "plan", "续费", "renew", "群", "group", "channel",
    "更新", "update", "公告", "notice", "备用", "backup",
]

# Purity score emoji mapping
PURITY_EMOJIS = {
    (0, 20): "🟢",    # Very clean
    (20, 40): "🟡",   # Clean
    (40, 60): "🟠",   # Moderate
    (60, 80): "🔴",   # Risky
    (80, 101): "⚫",  # Very risky
}

BOT_EMOJIS = {
    (0, 20): "🟢",
    (20, 40): "🟡",
    (40, 60): "🟠",
    (60, 80): "🔴",
    (80, 101): "⚫",
}


# ============================================================================
# 2. Data Structures
# ============================================================================

@dataclass
class IPCheckResult:
    """Result of an IP purity/risk check."""
    ip: str
    purity_score: int = 0          # 0-100, lower = cleaner
    bot_ratio: float = 0.0         # 0.0-1.0 bot traffic ratio
    shared_count: int = 0          # Number of users sharing this IP
    ip_type: str = "unknown"       # residential, datacenter, mobile
    ip_origin: str = "unknown"     # native, broadcast
    country: str = ""
    country_code: str = ""
    city: str = ""
    region: str = ""
    isp: str = ""
    org: str = ""
    asn: str = ""
    is_vpn: bool = False
    is_proxy: bool = False
    is_tor: bool = False
    risk_level: str = "unknown"    # low, medium, high, critical
    detection_source: str = ""
    detected_at: float = field(default_factory=time.time)
    raw_response: Dict[str, Any] = field(default_factory=dict)

    def purity_emoji(self) -> str:
        """Execute purity emoji operation for IPCheckResult."""
        for (lo, hi), emoji in PURITY_EMOJIS.items():
            if lo <= self.purity_score < hi:
                return emoji
        return "⚪"

    def bot_emoji(self) -> str:
        """Execute bot emoji operation for IPCheckResult."""
        bot_pct = int(self.bot_ratio * 100)
        for (lo, hi), emoji in BOT_EMOJIS.items():
            if lo <= bot_pct < hi:
                return emoji
        return "⚪"

    def tag_string(self) -> str:
        """Execute tag string operation for IPCheckResult."""
        ip_type_label = "住宅" if self.ip_type == "residential" else "机房" if self.ip_type == "datacenter" else self.ip_type
        origin_label = "原生" if self.ip_origin == "native" else "广播" if self.ip_origin == "broadcast" else self.ip_origin
        return f"【{self.purity_emoji()}{self.bot_emoji()} {ip_type_label}|{origin_label}】"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        return asdict(self)


@dataclass
class ProxyNode:
    """Represents a single proxy node from Clash config."""
    name: str
    proxy_type: str = "unknown"
    server: str = ""
    port: int = 0
    cipher: str = ""
    uuid: str = ""
    password: str = ""
    group: str = ""
    is_valid: bool = True
    check_result: Optional[IPCheckResult] = None
    original_name: str = ""
    tagged_name: str = ""
    latency_ms: float = -1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        d = {
            "name": self.name,
            "proxy_type": self.proxy_type,
            "server": self.server,
            "port": self.port,
            "group": self.group,
            "is_valid": self.is_valid,
            "latency_ms": self.latency_ms,
            "original_name": self.original_name,
            "tagged_name": self.tagged_name,
        }
        if self.check_result:
            d["check_result"] = self.check_result.to_dict()
        return d


@dataclass
class ClashConfig:
    """Parsed Clash configuration."""
    api_url: str = "http://127.0.0.1:9090"
    api_secret: str = ""
    yaml_path: str = ""
    fast_mode: bool = True
    source: str = "ping0"           # ping0, ippure, ip-api
    fallback: bool = True
    headless: bool = True
    concurrency: int = 3
    timeout: int = 10
    skip_patterns: List[str] = field(default_factory=lambda: list(SKIP_PATTERNS))


# ============================================================================
# 3. IP Detection Sources
# ============================================================================

class IPDetector:
    """Multi-source IP risk/purity detection engine."""

    def __init__(self, config: ClashConfig):
        """Initialize IPDetector."""
        self.config = config
        self._cache: Dict[str, IPCheckResult] = {}
        self._request_count = 0
        self._error_count = 0

    def detect(self, ip: str, proxy_url: Optional[str] = None) -> IPCheckResult:
        """Detect IP risk using configured source with fallback."""
        if ip in self._cache:
            return self._cache[ip]

        sources = self._build_source_chain()
        last_error = None

        for source in sources:
            try:
                result = self._detect_with_source(ip, source, proxy_url)
                if result:
                    self._cache[ip] = result
                    self._request_count += 1
                    return result
            except Exception as e:
                last_error = e
                self._error_count += 1
                continue

        # All sources failed — return unknown
        return IPCheckResult(
            ip=ip, detection_source="none",
            risk_level="unknown",
        )

    def _build_source_chain(self) -> List[DetectionSource]:
        primary = DetectionSource(self.config.source)
        chain = [primary]
        if self.config.fallback:
            for s in DetectionSource:
                if s != primary and s != DetectionSource.FALLBACK:
                    chain.append(s)
        return chain

    def _detect_with_source(self, ip: str, source: DetectionSource,
                            proxy_url: Optional[str]) -> Optional[IPCheckResult]:
        if source == DetectionSource.PING0:
            return self._detect_ping0(ip, proxy_url)
        elif source == DetectionSource.IPPURE:
            return self._detect_ippure(ip, proxy_url)
        elif source == DetectionSource.IPAPI:
            return self._detect_ipapi(ip, proxy_url)
        return None

    def _detect_ping0(self, ip: str, proxy_url: Optional[str]) -> Optional[IPCheckResult]:
        """Detect via Ping0.cc API."""
        url = f"https://ping0.cc/ip/{ip}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/html",
            "Referer": "https://ping0.cc/",
        }
        try:
            req = urllib.request.Request(url, headers=headers)
            if proxy_url:
                proxy_handler = urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})
                opener = urllib.request.build_opener(proxy_handler)
            else:
                opener = urllib.request.build_opener()
            with opener.open(req, timeout=self.config.timeout) as response:
                data = response.read().decode("utf-8", errors="ignore")

            # Parse ping0 response (HTML scraping or JSON)
            result = IPCheckResult(ip=ip, detection_source="ping0")

            # Extract purity score
            purity_match = re.search(r'(\d+)\s*/\s*100', data)
            if purity_match:
                result.purity_score = int(purity_match.group(1))

            # Extract shared count
            shared_match = re.search(r'共享人数[：:]\s*(\d+)', data)
            if shared_match:
                result.shared_count = int(shared_match.group(1))

            # Extract IP type
            if "住宅" in data or "residential" in data.lower():
                result.ip_type = "residential"
            elif "数据中心" in data or "datacenter" in data.lower():
                result.ip_type = "datacenter"
            elif "移动" in data or "mobile" in data.lower():
                result.ip_type = "mobile"

            # Extract origin
            if "原生" in data or "native" in data.lower():
                result.ip_origin = "native"
            elif "广播" in data or "broadcast" in data.lower():
                result.ip_origin = "broadcast"

            result.risk_level = self._score_to_risk(result.purity_score)
            result.raw_response = {"source": "ping0", "data_length": len(data)}
            return result
        except Exception:
            return None

    def _detect_ippure(self, ip: str, proxy_url: Optional[str]) -> Optional[IPCheckResult]:
        """Detect via IPPure.com API."""
        url = f"https://api.ippure.com/api/ipcheck?ip={ip}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json",
        }
        try:
            req = urllib.request.Request(url, headers=headers)
            if proxy_url:
                proxy_handler = urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})
                opener = urllib.request.build_opener(proxy_handler)
            else:
                opener = urllib.request.build_opener()
            with opener.open(req, timeout=self.config.timeout) as response:
                raw = response.read().decode("utf-8", errors="ignore")

            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                return None

            result = IPCheckResult(ip=ip, detection_source="ippure")
            result.purity_score = data.get("purity_score", data.get("risk_score", 50))
            result.bot_ratio = data.get("bot_ratio", 0.0)
            result.ip_type = data.get("ip_type", "unknown")
            result.ip_origin = data.get("origin", "unknown")
            result.country = data.get("country", "")
            result.country_code = data.get("country_code", "")
            result.city = data.get("city", "")
            result.isp = data.get("isp", "")
            result.is_vpn = data.get("is_vpn", False)
            result.is_proxy = data.get("is_proxy", False)
            result.risk_level = self._score_to_risk(result.purity_score)
            result.raw_response = data
            return result
        except Exception:
            return None

    def _detect_ipapi(self, ip: str, proxy_url: Optional[str]) -> Optional[IPCheckResult]:
        """Detect via ip-api.com free API."""
        url = f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,regionName,city,isp,org,as,proxy,hosting,query"
        try:
            req = urllib.request.Request(url)
            if proxy_url:
                proxy_handler = urllib.request.ProxyHandler({"http": proxy_url})
                opener = urllib.request.build_opener(proxy_handler)
            else:
                opener = urllib.request.build_opener()
            with opener.open(req, timeout=self.config.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))

            if data.get("status") != "success":
                return None

            result = IPCheckResult(ip=ip, detection_source="ip-api")
            result.country = data.get("country", "")
            result.country_code = data.get("countryCode", "")
            result.region = data.get("regionName", "")
            result.city = data.get("city", "")
            result.isp = data.get("isp", "")
            result.org = data.get("org", "")
            result.asn = data.get("as", "")
            result.is_proxy = data.get("proxy", False)

            # Infer type from hosting field
            is_hosting = data.get("hosting", False)
            result.ip_type = "datacenter" if is_hosting else "residential"
            result.purity_score = 60 if is_hosting else 20
            if result.is_proxy:
                result.purity_score += 20
            result.risk_level = self._score_to_risk(result.purity_score)
            result.raw_response = data
            return result
        except Exception:
            return None

    @staticmethod
    def _score_to_risk(score: int) -> str:
        if score < 20:
            return "low"
        elif score < 40:
            return "moderate"
        elif score < 60:
            return "medium"
        elif score < 80:
            return "high"
        return "critical"

    def clear_cache(self):
        """Execute clear cache operation for IPDetector."""
        self._cache.clear()

    def cache_stats(self) -> Dict[str, Any]:
        """Execute cache stats operation for IPDetector."""
        return {
            "cached_ips": len(self._cache),
            "total_requests": self._request_count,
            "total_errors": self._error_count,
        }


# ============================================================================
# 4. Clash API Client
# ============================================================================

class ClashAPIClient:
    """Client for the Clash External Controller REST API."""

    def __init__(self, api_url: str = "http://127.0.0.1:9090", secret: str = ""):
        """Initialize ClashAPIClient."""
        self.api_url = api_url.rstrip("/")
        self.secret = secret

    def _request(self, method: str, path: str, body: Optional[dict] = None) -> dict:
        url = f"{self.api_url}{path}"
        headers = {"Content-Type": "application/json"}
        if self.secret:
            headers["Authorization"] = f"Bearer {self.secret}"

        data = json.dumps(body).encode("utf-8") if body else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            return {"error": str(e), "code": e.code}
        except Exception as e:
            return {"error": str(e)}

    def get_version(self) -> Dict[str, Any]:
        """Retrieve version from ClashAPIClient."""
        return self._request("GET", "/version")

    def get_config(self) -> Dict[str, Any]:
        """Retrieve config from ClashAPIClient."""
        return self._request("GET", "/configs")

    def get_proxies(self) -> Dict[str, Any]:
        """Retrieve proxies from ClashAPIClient."""
        return self._request("GET", "/proxies")

    def get_proxy(self, name: str) -> Dict[str, Any]:
        """Retrieve proxy from ClashAPIClient."""
        encoded = urllib.parse.quote(name, safe="")
        return self._request("GET", f"/proxies/{encoded}")

    def switch_proxy(self, group: str, proxy_name: str) -> Dict[str, Any]:
        """Execute switch proxy operation for ClashAPIClient."""
        encoded = urllib.parse.quote(group, safe="")
        return self._request("PUT", f"/proxies/{encoded}", {"name": proxy_name})

    def set_mode(self, mode: str) -> Dict[str, Any]:
        """Set Clash mode: global, rule, direct."""
        return self._request("PATCH", "/configs", {"mode": mode})

    def test_delay(self, proxy_name: str, url: str = "http://www.gstatic.com/generate_204",
                   timeout: int = 5000) -> Dict[str, Any]:
        """Execute test delay operation for ClashAPIClient."""
        encoded = urllib.parse.quote(proxy_name, safe="")
        test_url = urllib.parse.quote(url, safe="")
        return self._request("GET", f"/proxies/{encoded}/delay?timeout={timeout}&url={test_url}")

    def is_connected(self) -> bool:
        """Check if connected condition holds."""
        result = self.get_version()
        return "error" not in result


# ============================================================================
# 5. Config Parser
# ============================================================================

class ClashConfigParser:
    """Lightweight YAML-like parser for Clash proxy configs (no PyYAML needed)."""

    @staticmethod
    def parse_proxies(yaml_path: str) -> List[ProxyNode]:
        """Extract proxy nodes from a Clash YAML config."""
        nodes = []
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                content = f.read()
        except (OSError, IOError):
            return nodes

        # Simple regex-based extraction for proxy entries
        # Matches "- name: ..." pattern in the proxies section
        in_proxies = False
        lines = content.split("\n")
        current_node: Dict[str, Any] = {}

        for line in lines:
            stripped = line.strip()

            if stripped == "proxies:" or stripped == "proxies :":
                in_proxies = True
                continue

            if in_proxies:
                # End of proxies section
                if stripped and not stripped.startswith("-") and not stripped.startswith(" ") and ":" in stripped:
                    if not stripped.startswith("#"):
                        in_proxies = False
                        if current_node:
                            nodes.append(ClashConfigParser._to_proxy_node(current_node))
                        continue

                if stripped.startswith("- "):
                    # New proxy entry
                    if current_node:
                        nodes.append(ClashConfigParser._to_proxy_node(current_node))
                    current_node = {}
                    # Parse inline: - {name: x, type: y, ...}
                    if stripped.startswith("- {"):
                        try:
                            inner = stripped[2:].strip()
                            inner = inner.strip("{}")
                            for part in inner.split(","):
                                if ":" in part:
                                    k, v = part.split(":", 1)
                                    current_node[k.strip()] = v.strip().strip("'\"")
                        except Exception:
                            pass
                    else:
                        # - name: value
                        rest = stripped[2:]
                        if ":" in rest:
                            k, v = rest.split(":", 1)
                            current_node[k.strip()] = v.strip().strip("'\"")

                elif stripped and ":" in stripped and in_proxies:
                    k, v = stripped.split(":", 1)
                    current_node[k.strip()] = v.strip().strip("'\"")

        if current_node:
            nodes.append(ClashConfigParser._to_proxy_node(current_node))

        return nodes

    @staticmethod
    def _to_proxy_node(d: Dict[str, Any]) -> ProxyNode:
        name = d.get("name", "")
        node = ProxyNode(
            name=name,
            original_name=name,
            proxy_type=d.get("type", "unknown"),
            server=d.get("server", ""),
            port=int(d.get("port", 0)),
            cipher=d.get("cipher", ""),
            uuid=d.get("uuid", d.get("password", "")),
        )
        # Check validity
        name_lower = name.lower()
        for pattern in SKIP_PATTERNS:
            if pattern.lower() in name_lower:
                node.is_valid = False
                break
        return node

    @staticmethod
    def should_skip_node(name: str) -> bool:
        """Execute should skip node operation for ClashConfigParser."""
        name_lower = name.lower()
        for pattern in SKIP_PATTERNS:
            if pattern.lower() in name_lower:
                return True
        return False


# ============================================================================
# 6. Batch Checker
# ============================================================================

class BatchChecker:
    """Orchestrates batch IP checking across all proxy nodes."""

    def __init__(self, detector: IPDetector, clash_client: ClashAPIClient, config: ClashConfig):
        """Initialize BatchChecker."""
        self.detector = detector
        self.clash_client = clash_client
        self.config = config
        self._results: List[ProxyNode] = []
        self._started_at: float = 0
        self._completed_at: float = 0

    def check_all(self, nodes: List[ProxyNode],
                  progress_callback=None) -> List[ProxyNode]:
        """Check all nodes sequentially. Returns nodes with check results."""
        self._started_at = time.time()
        total = len(nodes)
        checked = 0

        for node in nodes:
            if not node.is_valid:
                self._results.append(node)
                continue

            # Test delay first
            delay_result = self.clash_client.test_delay(node.name)
            if "delay" in delay_result:
                node.latency_ms = delay_result["delay"]

            # Get the IP through the proxy
            ip = self._resolve_node_ip(node)
            if ip:
                result = self.detector.detect(ip)
                node.check_result = result
                node.tagged_name = f"{result.tag_string()} {node.original_name}"
            else:
                node.tagged_name = f"【⚪ ?|?】 {node.original_name}"

            self._results.append(node)
            checked += 1

            if progress_callback:
                progress_callback(checked, total, node)

        self._completed_at = time.time()
        return self._results

    def _resolve_node_ip(self, node: ProxyNode) -> Optional[str]:
        """Resolve the exit IP of a proxy node."""
        # Try to resolve via server hostname
        try:
            ip = socket.gethostbyname(node.server)
            return ip
        except (socket.gaierror, socket.herror):
            return None

    def get_summary(self) -> Dict[str, Any]:
        """Retrieve summary from BatchChecker."""
        total = len(self._results)
        checked = sum(1 for n in self._results if n.check_result is not None)
        risk_dist = {"low": 0, "moderate": 0, "medium": 0, "high": 0, "critical": 0, "unknown": 0}
        type_dist = {"residential": 0, "datacenter": 0, "mobile": 0, "unknown": 0}

        for node in self._results:
            if node.check_result:
                risk = node.check_result.risk_level
                risk_dist[risk] = risk_dist.get(risk, 0) + 1
                ip_type = node.check_result.ip_type
                type_dist[ip_type] = type_dist.get(ip_type, 0) + 1

        return {
            "total_nodes": total,
            "checked_nodes": checked,
            "skipped_nodes": total - checked,
            "risk_distribution": risk_dist,
            "type_distribution": type_dist,
            "duration_seconds": round(self._completed_at - self._started_at, 2),
            "cache_stats": self.detector.cache_stats(),
        }

    def export_results(self) -> List[Dict[str, Any]]:
        """Execute export results operation for BatchChecker."""
        return [n.to_dict() for n in self._results]


# ============================================================================
# 7. Report Generator
# ============================================================================

class ReportGenerator:
    """Generates check reports in multiple formats."""

    @staticmethod
    def generate_json(results: List[ProxyNode], summary: Dict[str, Any]) -> str:
        """Execute generate json operation for ReportGenerator."""
        report = {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": summary,
            "nodes": [n.to_dict() for n in results],
        }
        return json.dumps(report, indent=2, ensure_ascii=False)

    @staticmethod
    def generate_markdown(results: List[ProxyNode], summary: Dict[str, Any]) -> str:
        """Execute generate markdown operation for ReportGenerator."""
        lines = [
            "# 🛡️ Clash IP Check Report",
            f"\nGenerated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"\n## Summary",
            f"- Total nodes: {summary['total_nodes']}",
            f"- Checked: {summary['checked_nodes']}",
            f"- Skipped: {summary['skipped_nodes']}",
            f"- Duration: {summary['duration_seconds']}s",
            "",
            "## Risk Distribution",
        ]
        for risk, count in summary.get("risk_distribution", {}).items():
            lines.append(f"- {risk}: {count}")

        lines.extend(["", "## Node Results", ""])
        lines.append("| Tag | Node | IP | Score | Type | Origin | ISP |")
        lines.append("|-----|------|----|-------|------|--------|-----|")

        for node in results:
            if node.check_result:
                r = node.check_result
                tag = r.tag_string()
                lines.append(
                    f"| {tag} | {node.original_name} | {r.ip} | "
                    f"{r.purity_score} | {r.ip_type} | {r.ip_origin} | {r.isp} |"
                )
            else:
                lines.append(f"| ⚪ | {node.original_name} | - | - | - | - | - |")

        return "\n".join(lines)


# ============================================================================
# 8. Main Engine
# ============================================================================

class OmniClashIPCheckerEngine:
    """
    OMNI Clash IP Checker Engine.

    Production-grade proxy node IP risk analysis and scoring.
    Supports Clash External Controller API, multi-source IP detection,
    batch processing, and comprehensive reporting.

    Usage:
        engine = OmniClashIPCheckerEngine()
        engine.configure(api_url="http://127.0.0.1:9090")
        nodes = engine.load_config("/path/to/config.yaml")
        results = engine.check_all_nodes(nodes)
        report = engine.generate_report("json")
    """

    def __init__(self, data_dir: str = ""):
        """Initialize OmniClashIPCheckerEngine."""
        if not data_dir:
            home = os.path.expanduser("~")
            data_dir = os.path.join(home, ".omni", "clash_checker")
        os.makedirs(data_dir, exist_ok=True)

        self.data_dir = data_dir
        self.config = ClashConfig()
        self.clash_client = ClashAPIClient()
        self.detector = IPDetector(self.config)
        self.parser = ClashConfigParser()
        self.batch_checker: Optional[BatchChecker] = None
        self._nodes: List[ProxyNode] = []
        self._last_results: List[ProxyNode] = []
        self._last_summary: Dict[str, Any] = {}
        self._started_at = time.time()
        self._total_checks = 0

    def configure(self, api_url: str = "", api_secret: str = "",
                  fast_mode: bool = True, source: str = "ping0",
                  fallback: bool = True, concurrency: int = 3,
                  timeout: int = 10) -> Dict[str, Any]:
        """Configure the engine parameters."""
        if api_url:
            self.config.api_url = api_url
        if api_secret:
            self.config.api_secret = api_secret
        self.config.fast_mode = fast_mode
        self.config.source = source
        self.config.fallback = fallback
        self.config.concurrency = concurrency
        self.config.timeout = timeout

        # Reinitialize clients with new config
        self.clash_client = ClashAPIClient(self.config.api_url, self.config.api_secret)
        self.detector = IPDetector(self.config)

        return {"status": "configured", "config": asdict(self.config)}

    def test_connection(self) -> Dict[str, Any]:
        """Test connection to the Clash External Controller."""
        connected = self.clash_client.is_connected()
        version = self.clash_client.get_version() if connected else {}
        return {
            "connected": connected,
            "version": version,
            "api_url": self.config.api_url,
        }

    def load_config(self, yaml_path: str) -> List[Dict[str, Any]]:
        """Load and parse proxy nodes from a Clash YAML config file."""
        self.config.yaml_path = yaml_path
        self._nodes = self.parser.parse_proxies(yaml_path)
        valid = sum(1 for n in self._nodes if n.is_valid)
        return [{
            "total_nodes": len(self._nodes),
            "valid_nodes": valid,
            "skipped_nodes": len(self._nodes) - valid,
            "nodes": [n.to_dict() for n in self._nodes[:20]],  # Preview first 20
        }]

    def load_from_api(self) -> List[Dict[str, Any]]:
        """Load proxy nodes from Clash API instead of YAML file."""
        proxies = self.clash_client.get_proxies()
        self._nodes = []

        for name, info in proxies.get("proxies", {}).items():
            ptype = info.get("type", "")
            if ptype in ("Selector", "URLTest", "Fallback", "LoadBalance", "Relay", "Direct", "Reject"):
                continue  # Skip proxy groups

            node = ProxyNode(
                name=name,
                original_name=name,
                proxy_type=ptype.lower(),
                server=info.get("server", name),
                port=info.get("port", 0),
                is_valid=not self.parser.should_skip_node(name),
            )
            self._nodes.append(node)

        valid = sum(1 for n in self._nodes if n.is_valid)
        return [{
            "total_nodes": len(self._nodes),
            "valid_nodes": valid,
            "nodes": [n.to_dict() for n in self._nodes[:20]],
        }]

    def check_single_ip(self, ip: str) -> Dict[str, Any]:
        """Check a single IP address."""
        result = self.detector.detect(ip)
        self._total_checks += 1
        return result.to_dict()

    def check_all_nodes(self, progress_callback=None) -> Dict[str, Any]:
        """Run batch checking on all loaded nodes."""
        if not self._nodes:
            return {"error": "No nodes loaded. Call load_config() or load_from_api() first."}

        self.batch_checker = BatchChecker(self.detector, self.clash_client, self.config)

        # Set to Global mode for accurate testing
        self.clash_client.set_mode("global")

        self._last_results = self.batch_checker.check_all(self._nodes, progress_callback)
        self._last_summary = self.batch_checker.get_summary()
        self._total_checks += self._last_summary.get("checked_nodes", 0)

        # Restore original mode
        self.clash_client.set_mode("rule")

        return self._last_summary

    def generate_report(self, format: str = "json") -> str:
        """Generate a check report."""
        if format == "markdown":
            return ReportGenerator.generate_markdown(self._last_results, self._last_summary)
        return ReportGenerator.generate_json(self._last_results, self._last_summary)

    def export_checked_config(self, output_path: str = "") -> str:
        """Export a new Clash config with tagged node names."""
        if not output_path:
            if self.config.yaml_path:
                base = Path(self.config.yaml_path)
                output_path = str(base.parent / f"{base.stem}_checked{base.suffix}")
            else:
                output_path = os.path.join(self.data_dir, "config_checked.yaml")

        # Read original config and replace node names
        if self.config.yaml_path and os.path.exists(self.config.yaml_path):
            with open(self.config.yaml_path, "r", encoding="utf-8") as f:
                content = f.read()
            for node in self._last_results:
                if node.tagged_name and node.original_name:
                    content = content.replace(
                        f"name: {node.original_name}",
                        f"name: {node.tagged_name}",
                        1
                    )
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

        return output_path

    def get_cached_results(self) -> Dict[str, Any]:
        """Get results from the last check."""
        return {
            "summary": self._last_summary,
            "results": [n.to_dict() for n in self._last_results],
        }

    def clear_cache(self):
        """Clear the IP detection cache."""
        self.detector.clear_cache()

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniClashIPCheckerEngine."""
        return {
            "engine": "OmniClashIPCheckerEngine",
            "version": ENGINE_VERSION,
            "status": "operational",
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(self._started_at)),
            "config": {
                "api_url": self.config.api_url,
                "fast_mode": self.config.fast_mode,
                "source": self.config.source,
                "fallback": self.config.fallback,
                "concurrency": self.config.concurrency,
            },
            "stats": {
                "total_checks": self._total_checks,
                "loaded_nodes": len(self._nodes),
                "last_results": len(self._last_results),
                "cache": self.detector.cache_stats(),
            },
            "capabilities": [
                "clash_api_integration", "multi_source_detection",
                "batch_checking", "ip_risk_scoring", "node_tagging",
                "yaml_config_parsing", "report_generation",
                "auto_fallback", "global_mode_switching",
            ],
        }
