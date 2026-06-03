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
        sys.executable, "-m", "uvicorn",
        "app.api.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
    ]
    subprocess.run(cmd, cwd=str(PROJECT_ROOT), env=env)

if __name__ == "__main__":
    main()
