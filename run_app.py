#!/usr/bin/env python
"""
CrisisLens Dashboard Wrapper

Runs the Streamlit dashboard with proper module path configuration.
"""

import sys
import subprocess
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Run streamlit with proper environment
dashboard_path = project_root / "app" / "dashboard" / "app.py"

# Set up environment with PYTHONPATH
env = os.environ.copy()
env["PYTHONPATH"] = str(project_root)

cmd = [
    sys.executable,
    "-m",
    "streamlit",
    "run",
    str(dashboard_path),
    "--server.port",
    "8501",
    "--server.address",
    "localhost",
]

subprocess.run(cmd, cwd=str(project_root), env=env)
