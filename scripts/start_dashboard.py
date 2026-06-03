from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def main() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(PROJECT_ROOT / "app" / "dashboard" / "app.py"),
        "--server.port", "8501",
        "--server.address", "localhost",
    ]
    subprocess.run(cmd, cwd=str(PROJECT_ROOT), env=env)

if __name__ == "__main__":
    main()
