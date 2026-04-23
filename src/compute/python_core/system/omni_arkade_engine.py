ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI ARKADE ENGINE — Kubernetes App Marketplace & CLI Installer
# ===========================================================================
# Source Paradigm: https://github.com/alexellis/arkade
# Domain Layer  : System / Kubernetes Cluster
# Zero-Prod     : 100% Native — subprocess, urllib, os filesystem operations
# ===========================================================================
"""
Arkade teaches us:
  1. One-line CLI install of k8s apps (helm charts + manifests)
  2. Cross-platform binary downloading (kubectl, helm, faas-cli, etc.)
  3. App catalog as structured data with version pinning
  4. Checksum verification for downloaded binaries
  5. Environment detection (arch, os) for correct binary selection

This engine distills those paradigms into an OMNI-native tool installer
and Kubernetes app catalog manager using ONLY stdlib.
"""

import hashlib
import json
import os
import platform
import shutil
import subprocess
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ── Data Models ──────────────────────────────────────────────────────────────

@dataclass
class ToolSpec:
    """OMNI production engine for ToolSpec integration."""
    name: str
    description: str
    version: str
    url_template: str      # uses {os}, {arch}, {version} placeholders
    binary_name: str
    sha256: str = ""       # expected checksum (empty = skip verify)
    post_install: str = "" # shell command to run after install

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "ToolSpec",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


@dataclass
class K8sApp:
    """OMNI production engine for K8sApp integration."""
    name: str
    description: str
    namespace: str = "default"
    helm_repo: str = ""
    helm_chart: str = ""
    manifest_url: str = ""
    values_override: Dict[str, str] = field(default_factory=dict)

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "K8sApp",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


# ── Platform Detection ──────────────────────────────────────────────────────

class PlatformDetector:
    """Detect OS and architecture for correct binary selection."""

    @staticmethod
    def detect() -> Tuple[str, str]:
        """Execute detect operation for PlatformDetector engine."""
        sys_os = platform.system().lower()
        arch = platform.machine().lower()

        # Normalize OS
        os_map = {"windows": "windows", "linux": "linux", "darwin": "darwin"}
        norm_os = os_map.get(sys_os, sys_os)

        # Normalize arch
        arch_map = {
            "x86_64": "amd64", "amd64": "amd64",
            "aarch64": "arm64", "arm64": "arm64",
            "armv7l": "armhf",
        }
        norm_arch = arch_map.get(arch, arch)

        return norm_os, norm_arch

    @staticmethod
    def binary_extension() -> str:
        """Execute binary extension operation for PlatformDetector engine."""
        return ".exe" if platform.system().lower() == "windows" else ""

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "PlatformDetector",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


# ── Tool Catalog (Built-in Marketplace) ──────────────────────────────────────

class ToolCatalog:
    """Built-in catalog of essential DevOps/K8s tools."""

    TOOLS: Dict[str, ToolSpec] = {
        "kubectl": ToolSpec(
            name="kubectl",
            description="Kubernetes CLI tool",
            version="v1.31.0",
            url_template="https://dl.k8s.io/release/{version}/bin/{os}/{arch}/kubectl{ext}",
            binary_name="kubectl",
        ),
        "helm": ToolSpec(
            name="helm",
            description="Kubernetes package manager",
            version="v3.16.0",
            url_template="https://get.helm.sh/helm-{version}-{os}-{arch}.tar.gz",
            binary_name="helm",
        ),
        "k9s": ToolSpec(
            name="k9s",
            description="Terminal dashboard for Kubernetes",
            version="v0.32.0",
            url_template="https://github.com/derailed/k9s/releases/download/{version}/k9s_{os}_{arch}.tar.gz",
            binary_name="k9s",
        ),
        "kubectx": ToolSpec(
            name="kubectx",
            description="Switch between kubectl contexts faster",
            version="v0.9.5",
            url_template="https://github.com/ahmetb/kubectx/releases/download/{version}/kubectx_{version}_{os}_{arch}.tar.gz",
            binary_name="kubectx",
        ),
    }

    K8S_APPS: Dict[str, K8sApp] = {
        "nginx-ingress": K8sApp(
            name="nginx-ingress",
            description="NGINX Ingress Controller for Kubernetes",
            namespace="ingress-nginx",
            helm_repo="https://kubernetes.github.io/ingress-nginx",
            helm_chart="ingress-nginx/ingress-nginx",
        ),
        "cert-manager": K8sApp(
            name="cert-manager",
            description="Automated TLS certificate management",
            namespace="cert-manager",
            manifest_url="https://github.com/cert-manager/cert-manager/releases/download/v1.15.0/cert-manager.yaml",
        ),
        "metrics-server": K8sApp(
            name="metrics-server",
            description="Cluster resource metrics collection",
            namespace="kube-system",
            manifest_url="https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml",
        ),
        "prometheus": K8sApp(
            name="prometheus",
            description="Monitoring and alerting toolkit",
            namespace="monitoring",
            helm_repo="https://prometheus-community.github.io/helm-charts",
            helm_chart="prometheus-community/prometheus",
        ),
    }

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "ToolCatalog",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


# ── Tool Installer ──────────────────────────────────────────────────────────

class ToolInstaller:
    """Downloads and installs CLI tools natively."""

    def __init__(self, install_dir: str = ""):
        """Initialize ToolInstaller engine with default configuration."""
        if not install_dir:
            install_dir = os.path.join(os.path.dirname(__file__), "..", ".arkade_bin")
        self.install_dir = install_dir
        os.makedirs(self.install_dir, exist_ok=True)

    def is_installed(self, tool_name: str) -> bool:
        """Execute is installed operation for ToolInstaller engine."""
        ext = PlatformDetector.binary_extension()
        path = os.path.join(self.install_dir, tool_name + ext)
        return os.path.isfile(path)

    def check_system_tool(self, tool_name: str) -> Optional[str]:
        """Check if a tool is already available on PATH."""
        which_cmd = "where" if platform.system() == "Windows" else "which"
        try:
            result = subprocess.run(
                [which_cmd, tool_name],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip().split("\n")[0]
        except Exception:
            pass
        return None

    def download_tool(self, spec: ToolSpec) -> Dict:
        """Download a tool binary from its URL template."""
        det_os, det_arch = PlatformDetector.detect()
        ext = PlatformDetector.binary_extension()

        url = (spec.url_template
               .replace("{version}", spec.version)
               .replace("{os}", det_os)
               .replace("{arch}", det_arch)
               .replace("{ext}", ext))

        dest_path = os.path.join(self.install_dir, spec.binary_name + ext)

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "OMNI-Arkade/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()

            # Checksum verification
            if spec.sha256:
                actual_hash = hashlib.sha256(data).hexdigest()
                if actual_hash != spec.sha256:
                    return {"status": "error", "message": f"Checksum mismatch: expected {spec.sha256}, got {actual_hash}"}

            with open(dest_path, "wb") as f:
                f.write(data)

            # Make executable on unix
            if det_os != "windows":
                os.chmod(dest_path, 0o755)

            return {
                "status": "success",
                "tool": spec.name,
                "version": spec.version,
                "path": dest_path,
                "size_bytes": len(data),
            }
        except Exception as e:
            return {"status": "error", "tool": spec.name, "message": str(e)[:256]}

    def list_installed(self) -> List[Dict]:
        """List all tools installed in the arkade bin directory."""
        tools = []
        if os.path.isdir(self.install_dir):
            for f in os.listdir(self.install_dir):
                full = os.path.join(self.install_dir, f)
                if os.path.isfile(full):
                    tools.append({
                        "name": f,
                        "path": full,
                        "size_bytes": os.path.getsize(full),
                    })
        return tools

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "ToolInstaller",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


# ── K8s App Deployer ────────────────────────────────────────────────────────

class K8sAppDeployer:
    """Deploy Kubernetes apps via kubectl/helm subprocess calls."""

    @staticmethod
    def apply_manifest(manifest_url: str, namespace: str = "default") -> Dict:
        """Apply a Kubernetes manifest from a URL using kubectl."""
        try:
            result = subprocess.run(
                ["kubectl", "apply", "-f", manifest_url, "-n", namespace],
                capture_output=True, text=True, timeout=60,
            )
            return {
                "status": "success" if result.returncode == 0 else "error",
                "stdout": result.stdout[:2048],
                "stderr": result.stderr[:1024],
            }
        except FileNotFoundError:
            return {"status": "error", "message": "kubectl not found on PATH"}
        except Exception as e:
            return {"status": "error", "message": str(e)[:256]}

    @staticmethod
    def helm_install(app: K8sApp) -> Dict:
        """Install a Kubernetes app using Helm."""
        try:
            # Add repo
            if app.helm_repo:
                repo_name = app.helm_chart.split("/")[0] if "/" in app.helm_chart else app.name
                subprocess.run(
                    ["helm", "repo", "add", repo_name, app.helm_repo],
                    capture_output=True, text=True, timeout=30,
                )
                subprocess.run(["helm", "repo", "update"], capture_output=True, text=True, timeout=30)

            # Install chart
            cmd = ["helm", "install", app.name, app.helm_chart,
                   "--namespace", app.namespace, "--create-namespace"]
            for k, v in app.values_override.items():
                cmd.extend(["--set", f"{k}={v}"])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            return {
                "status": "success" if result.returncode == 0 else "error",
                "stdout": result.stdout[:2048],
                "stderr": result.stderr[:1024],
            }
        except FileNotFoundError:
            return {"status": "error", "message": "helm not found on PATH"}
        except Exception as e:
            return {"status": "error", "message": str(e)[:256]}

    def diagnostics(self):
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "K8sAppDeployer",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": []
        }


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniArkadeEngine:
    """
    OMNI Arkade Engine — Zero-Prod Kubernetes Marketplace & Tool Installer.

    Capabilities (all native stdlib):
      - Cross-platform tool detection (kubectl, helm, k9s, etc.)
      - Binary download with checksum verification
      - K8s app catalog (helm charts + manifests)
      - kubectl/helm subprocess deployment
      - Platform auto-detection (OS + arch)
    """

    def __init__(self):
        """Initialize Arkade engine with default configuration."""
        self.catalog = ToolCatalog()
        self.installer = ToolInstaller()
        self.deployer = K8sAppDeployer()

    def get_tool(self, name: str) -> Dict:
        """Check if a tool exists on system or in arkade bin."""
        sys_path = self.installer.check_system_tool(name)
        if sys_path:
            return {"status": "found", "location": "system", "path": sys_path}
        if self.installer.is_installed(name):
            return {"status": "found", "location": "arkade_bin",
                    "path": os.path.join(self.installer.install_dir, name)}
        return {"status": "not_found", "available": name in self.catalog.TOOLS}

    def install_tool(self, name: str) -> Dict:
        """Download and install a tool from the catalog."""
        if name not in self.catalog.TOOLS:
            return {"status": "error", "message": f"Tool '{name}' not in catalog"}
        return self.installer.download_tool(self.catalog.TOOLS[name])

    def deploy_app(self, name: str) -> Dict:
        """Deploy a K8s app from the catalog."""
        if name not in self.catalog.K8S_APPS:
            return {"status": "error", "message": f"App '{name}' not in catalog"}
        app = self.catalog.K8S_APPS[name]
        if app.manifest_url:
            return self.deployer.apply_manifest(app.manifest_url, app.namespace)
        elif app.helm_chart:
            return self.deployer.helm_install(app)
        return {"status": "error", "message": "No deployment method available"}

    def system_check(self) -> Dict:
        """Check which essential tools are available on this system."""
        det_os, det_arch = PlatformDetector.detect()
        tools_status = {}
        for name in self.catalog.TOOLS:
            path = self.installer.check_system_tool(name)
            tools_status[name] = {"installed": path is not None, "path": path or ""}
        return {
            "platform": {"os": det_os, "arch": det_arch},
            "tools": tools_status,
        }

    def diagnostics(self) -> Dict:
        """Return engine health status for the OmniEngineRegistry."""
        det_os, det_arch = PlatformDetector.detect()
        return {
            "engine": "OmniArkadeEngine",
            "status": "active",
            "platform": f"{det_os}/{det_arch}",
            "capabilities": ["tool_catalog", "binary_download", "checksum_verify",
                             "k8s_app_deploy", "system_tool_check"],
            "install_dir": self.installer.install_dir,
            "catalog_tools": list(self.catalog.TOOLS.keys()),
            "catalog_apps": list(self.catalog.K8S_APPS.keys()),
        }


if __name__ == "__main__":
    engine = OmniArkadeEngine()
    print("[Arkade] System Check:")
    check = engine.system_check()
    print(json.dumps(check, indent=2))
