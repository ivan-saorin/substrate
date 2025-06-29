#!/usr/bin/env python
"""Setup script for Substrate development environment (Windows)."""

import os
import sys
import subprocess
from pathlib import Path


def main():
    """Setup Substrate on Windows."""
    print("Substrate Development Setup (Windows)")
    print("====================================")
    
    project_path = Path(__file__).parent
    venv_path = project_path / "venv"
    
    # Create virtual environment
    if not venv_path.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], cwd=project_path, check=True)
    
    # Install dependencies
    pip_exe = str(venv_path / "Scripts" / "pip.exe")
    
    print("Upgrading pip...")
    subprocess.run([pip_exe, "install", "--upgrade", "pip"], cwd=project_path, check=True)
    
    print("Installing Substrate...")
    subprocess.run([pip_exe, "install", "-e", "."], cwd=project_path, check=True)
    
    print("Installing dev dependencies...")
    subprocess.run([pip_exe, "install", "-e", ".[dev]"], cwd=project_path, check=True)
    
    print("\nSetup complete!")
    print(f"Activate environment: {venv_path}\\Scripts\\activate.bat")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
