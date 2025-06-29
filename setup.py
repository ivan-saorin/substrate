#!/usr/bin/env python
"""Setup script for Substrate development environment."""

import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and handle errors."""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False


def main():
    """Setup Substrate development environment."""
    print("Substrate Development Setup")
    print("===========================")
    
    project_path = Path(__file__).parent
    
    # Create virtual environment if it doesn't exist
    venv_path = project_path / "venv"
    if not venv_path.exists():
        print("Creating virtual environment...")
        if not run_command([sys.executable, "-m", "venv", "venv"], cwd=project_path):
            return 1
            
    # Activate virtual environment and install
    if sys.platform == "win32":
        pip_cmd = [str(venv_path / "Scripts" / "pip.exe")]
        activate_cmd = str(venv_path / "Scripts" / "activate.bat")
    else:
        pip_cmd = [str(venv_path / "bin" / "pip")]
        activate_cmd = f"source {venv_path / 'bin' / 'activate'}"
        
    # Upgrade pip
    print("Upgrading pip...")
    run_command(pip_cmd + ["install", "--upgrade", "pip"], cwd=project_path)
    
    # Install project in editable mode
    print("Installing Substrate in editable mode...")
    if not run_command(pip_cmd + ["install", "-e", "."], cwd=project_path):
        return 1
        
    # Install dev dependencies
    print("Installing development dependencies...")
    run_command(pip_cmd + ["install", "-e", ".[dev]"], cwd=project_path)
    
    print("\nSetup Complete!")
    print(f"To activate the environment: {activate_cmd}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
