"""
OMNI Auto-Checkpoint System
===========================
Mekanisme pengamanan kode otomatis (Git Auto-Commit) untuk mengunci seluruh 
perkembangan OMNI ke dalam disk dan mencegah file hilang dari memori.

Didesain untuk dipanggil setiap kali sebuah batch/semester selesai di-generate.
"""
import subprocess
import logging
from datetime import datetime
import os
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("OmniCheckpoint")

def run_git_command(args, cwd=None):
    try:
        result = subprocess.run(
            args, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=False
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        logger.error(f"Failed to execute {' '.join(args)}: {e}")
        return -1, "", str(e)

def create_checkpoint(message=None):
    """Secure all code changes into Git."""
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    
    logger.info("Mempersiapkan OMNI Checkpoint...")

    # 1. Bypass the .scratch embedded git repo block
    logger.info(" Membersihkan index blockers...")
    run_git_command(["git", "rm", "--cached", "-r", "src/.scratch/"], cwd=root_dir)
    
    # 2. Stage ALL important directories explicitly
    target_dirs = [
        "src/compute/", 
        "src/domain/", 
        "src/network/", 
        "src/system/", 
        "src/ui/", 
        "src/scripts/",
        "tests/"
    ]
    
    for d in target_dirs:
        logger.info(f" Staging direktori: {d}")
        code, out, err = run_git_command(["git", "add", d], cwd=root_dir)
        if code != 0:
            logger.warning(f" Peringatan saat staging {d}: {err.strip()}")

    # 3. Check if there are things to commit
    code, out, err = run_git_command(["git", "status", "--porcelain"], cwd=root_dir)
    tracked_changes = [line for line in out.split("\n") if line.strip() and not line.startswith("??")]
    
    if not tracked_changes:
        logger.info(" Tidak ada perubahan baru. Workspace sudah aman dan tersimpan.")
        return True

    # 4. Commit changes
    commit_msg = message or f"OMNI Checkpoint: Auto-save layer engines and tests [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
    logger.info(f" Menyimpan {len(tracked_changes)} file(s) ke dalam node waktu...")
    code, out, err = run_git_command(["git", "commit", "-m", commit_msg], cwd=root_dir)

    if code == 0:
        logger.info("✅ POINT SELESAI. Seluruh OMNI Ecosystem sukses dikunci ke disk.")
        return True
    else:
        logger.error(f"❌ CHECKPOINT GAGAL:\n{out}\n{err}")
        return False

if __name__ == "__main__":
    import sys
    msg = sys.argv[1] if len(sys.argv) > 1 else None
    create_checkpoint(msg)
