# omni_advanced_executable.py
# Root Layer: OMNI Singularity Launcher — Full System Entrypoint
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Wires: Singularity Core + Hardware + VTube + Universal Deployer + Archon
# CLI:   python omni_advanced_executable.py [--deploy <platform>] [--superloop]
#        [--omi] [--vtube] [--audit <file>] [--platforms] [--help]
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import sys
sys.stdout.reconfigure(encoding='utf-8')
import time
import argparse
import os

# Ensure engine is importable
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "engine"))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Module Import Guards
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_MODULES = {}

def _try_import(name, import_fn):
    try:
        result = import_fn()
        _MODULES[name] = True
        return result
    except ImportError as e:
        _MODULES[name] = False
        return None

# Core
_try_import("singularity", lambda: __import__("omni_ai.singularity.omni_singularity_core", fromlist=["OmniSingularityCore"]))
_try_import("deployer", lambda: __import__("deploy.omni_universal_deployer", fromlist=["OmniUniversalDeployer"]))
_try_import("omi_bridge", lambda: __import__("hardware.omni_omi_webrtc_bridge", fromlist=["OmiWebRTCBridge"]))
_try_import("vtube_bridge", lambda: __import__("hardware.omni_vtube_studio_bridge", fromlist=["OmniVTubeBridge"]))
_try_import("archon", lambda: __import__("omni_ai.autonomy.omni_archon_superloop", fromlist=["ArchonSuperLoop", "MissionGoal"]))


def print_banner():
    print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 🪐 OMNI ADVANCED EXECUTABLE — SINGULARITY LAUNCHER v3.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Runtime   : OMNI-NEXUS / LLVM-Omni
 Languages : C · C++ · Rust · Go · JS · Python · Julia · R
             TypeScript · HTML · Swift · GraphQL · C# · Ruby · PHP
 Mode      : Architect-Class | Enterprise-Grade
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
    
    print("\n📦 Module Status:")
    icons = {True: "✅", False: "⬜"}
    for name, loaded in _MODULES.items():
        print(f"   {icons[loaded]} {name}")
    print()


def cmd_deploy(platform: str, app_name: str = "omni-framework"):
    """Deploy to a specific platform."""
    from deploy.omni_universal_deployer import OmniUniversalDeployer
    deployer = OmniUniversalDeployer(app_name=app_name)
    config = deployer.generate_config(platform)
    if config:
        print(f"\n📋 Generated config:\n{config[:500]}")
        print(f"\n🚀 Deploy command: {deployer.get_deploy_command(platform)}")


def cmd_platforms():
    """List all supported deployment platforms."""
    from deploy.omni_universal_deployer import OmniUniversalDeployer
    deployer = OmniUniversalDeployer()
    platforms = deployer.list_platforms()
    print(f"\n🌍 Supported Platforms ({len(platforms)}):\n")
    for p in platforms:
        free = " [FREE]" if p["free_tier"] else ""
        print(f"   {p['id']:15s} │ {p['name']}{free}")
        print(f"   {'':15s} │ {p['description']}")
        print(f"   {'':15s} │ Deploy: {p['deploy_command']}")
        print()


def cmd_omi():
    """Start Omi wearable bridge."""
    from hardware.omni_omi_webrtc_bridge import OmiWebRTCBridge
    bridge = OmiWebRTCBridge()
    bridge.start()


def cmd_vtube():
    """Start VTube Studio bridge."""
    from hardware.omni_vtube_studio_bridge import OmniVTubeBridge
    bridge = OmniVTubeBridge()
    bridge.start()


def cmd_superloop(goal_text: str = None):
    """Start Archon autonomous super-loop mission."""
    from omni_ai.autonomy.omni_archon_superloop import ArchonSuperLoop, MissionGoal
    
    goal = MissionGoal(
        goal_id="cli_mission",
        description=goal_text or "Self-optimize OMNI Framework for production readiness",
        success_criteria=[
            "Analyze codebase structure",
            "Run security audit",
            "Create deployment config",
            "Evaluate deployment health",
        ],
        target_score=70.0,
    )
    
    archon = ArchonSuperLoop(max_iterations=5, timeout_seconds=120.0)
    report = archon.execute_mission(goal)
    return report


def cmd_singularity():
    """Run full singularity cycle."""
    from omni_ai.singularity.omni_singularity_core import OmniSingularityCore
    core = OmniSingularityCore()
    core.full_singularity_cycle()


def cmd_default():
    """Default launch: quick system check."""
    print("🔧 Running system check...\n")
    
    print("[1] Singularity Core.........", end=" ")
    print("✅ ONLINE" if _MODULES.get("singularity") else "⬜ NOT LOADED")
    
    print("[2] Universal Deployer.......", end=" ")
    print("✅ ONLINE" if _MODULES.get("deployer") else "⬜ NOT LOADED")
    
    print("[3] Omi WebRTC Bridge........", end=" ")
    print("✅ ONLINE" if _MODULES.get("omi_bridge") else "⬜ NOT LOADED")
    
    print("[4] VTube Studio Bridge......", end=" ")
    print("✅ ONLINE" if _MODULES.get("vtube_bridge") else "⬜ NOT LOADED")
    
    print("[5] Archon Super-Loop........", end=" ")
    print("✅ ONLINE" if _MODULES.get("archon") else "⬜ NOT LOADED")
    
    print("\n🚀 OMNI SINGULARITY ENGINE: STANDING BY")
    print("   Use --help to see all commands")
    print("   Use --platforms to see deployment targets")
    print("   Use --superloop to start autonomous mission")


def main():
    parser = argparse.ArgumentParser(
        prog="omni",
        description="🪐 OMNI Advanced Executable — Singularity Launcher v3.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python omni_advanced_executable.py                    # System check
  python omni_advanced_executable.py --platforms        # List deploy targets
  python omni_advanced_executable.py --deploy railway   # Generate Railway config
  python omni_advanced_executable.py --deploy fly       # Generate Fly.io config
  python omni_advanced_executable.py --deploy vercel    # Generate Vercel config
  python omni_advanced_executable.py --omi              # Start Omi wearable bridge
  python omni_advanced_executable.py --vtube            # Start VTube Studio bridge
  python omni_advanced_executable.py --superloop        # Start Archon autonomous mission
  python omni_advanced_executable.py --singularity      # Full singularity cycle
        """
    )
    
    parser.add_argument("--deploy", type=str, metavar="PLATFORM",
                       help="Deploy to platform (docker, fly, railway, render, vercel, netlify, aws-ecs, azure, gcp, digitalocean, k8s, vps, coolify, caprover)")
    parser.add_argument("--platforms", action="store_true",
                       help="List all supported deployment platforms")
    parser.add_argument("--omi", action="store_true",
                       help="Start Omi wearable ↔ LeonAssistant WebRTC bridge")
    parser.add_argument("--vtube", action="store_true",
                       help="Start VTube Studio WebSocket bridge")
    parser.add_argument("--superloop", nargs="?", const="default", type=str,
                       help="Start Archon autonomous super-loop mission (optional: mission description)")
    parser.add_argument("--singularity", action="store_true",
                       help="Run full singularity cycle (all subsystems)")
    parser.add_argument("--app-name", type=str, default="omni-framework",
                       help="Application name for deployment (default: omni-framework)")
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.platforms:
        cmd_platforms()
    elif args.deploy:
        cmd_deploy(args.deploy, args.app_name)
    elif args.omi:
        cmd_omi()
    elif args.vtube:
        cmd_vtube()
    elif args.superloop:
        goal_text = args.superloop if args.superloop != "default" else None
        cmd_superloop(goal_text)
    elif args.singularity:
        cmd_singularity()
    else:
        cmd_default()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[SINGULARITY] Process interrupted. Fading out...")
        sys.exit(0)
