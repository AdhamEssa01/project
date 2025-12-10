"""
Setup script to fix virtual environment and install dependencies.

This script will:
1. Check for available Python installations
2. Recreate the virtual environment if needed
3. Install all required dependencies
"""

import os
import subprocess
import sys

def find_python():
    """Find available Python installation."""
    # Try common Python commands
    for cmd in ['python', 'python3', 'py']:
        try:
            result = subprocess.run([cmd, '--version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                print(f"[info] Found Python: {cmd}")
                print(f"[info] Version: {result.stdout.strip()}")
                return cmd
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return None

def recreate_venv(python_cmd):
    """Recreate virtual environment with available Python."""
    venv_path = "spacyenv"
    
    if os.path.exists(venv_path):
        print(f"[info] Removing old virtual environment...")
        import shutil
        try:
            shutil.rmtree(venv_path)
        except Exception as e:
            print(f"[warn] Could not remove old venv: {e}")
    
    print(f"[info] Creating new virtual environment with {python_cmd}...")
    result = subprocess.run([python_cmd, '-m', 'venv', venv_path],
                          capture_output=True,
                          text=True)
    
    if result.returncode != 0:
        print(f"[error] Failed to create virtual environment:")
        print(result.stderr)
        return False
    
    print("[info] Virtual environment created successfully")
    return True

def install_dependencies(python_cmd):
    """Install dependencies from requirements.txt."""
    if not os.path.exists("requirements.txt"):
        print("[error] requirements.txt not found")
        return False
    
    print("[info] Installing dependencies...")
    
    # Determine pip command based on Python command
    if python_cmd == 'py':
        pip_cmd = [python_cmd, '-m', 'pip']
    else:
        pip_cmd = [python_cmd, '-m', 'pip']
    
    # Upgrade pip first
    print("[info] Upgrading pip...")
    subprocess.run(pip_cmd + ['install', '--upgrade', 'pip'],
                  capture_output=True)
    
    # Install requirements
    print("[info] Installing packages from requirements.txt...")
    result = subprocess.run(pip_cmd + ['install', '-r', 'requirements.txt'],
                          capture_output=True,
                          text=True)
    
    if result.returncode != 0:
        print(f"[error] Failed to install dependencies:")
        print(result.stderr)
        return False
    
    print("[info] Dependencies installed successfully")
    return True

def main():
    print("=" * 60)
    print("Environment Setup Script")
    print("=" * 60)
    
    # Find Python
    python_cmd = find_python()
    if not python_cmd:
        print("[error] No Python installation found!")
        print("[error] Please install Python 3.8 or higher from python.org")
        return 1
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print("[info] Already in a virtual environment")
        # Install dependencies in current environment
        if install_dependencies(python_cmd):
            print("\n[success] Setup complete!")
            return 0
        else:
            return 1
    else:
        # Check if venv exists and is broken
        venv_python = os.path.join("spacyenv", "Scripts", "python.exe")
        if os.path.exists(venv_python):
            try:
                result = subprocess.run([venv_python, '--version'],
                                       capture_output=True,
                                       timeout=5)
                if result.returncode == 0:
                    print("[info] Virtual environment exists and works")
                    # Install dependencies in venv
                    if install_dependencies(venv_python):
                        print("\n[success] Setup complete!")
                        print("\n[info] To activate the virtual environment:")
                        print("  Windows: .\\spacyenv\\Scripts\\activate")
                        print("  Linux/Mac: source spacyenv/bin/activate")
                        return 0
            except:
                pass
        
        # Recreate venv
        if recreate_venv(python_cmd):
            # Install dependencies in new venv
            venv_python = os.path.join("spacyenv", "Scripts", "python.exe")
            if os.path.exists(venv_python):
                if install_dependencies(venv_python):
                    print("\n[success] Setup complete!")
                    print("\n[info] To activate the virtual environment:")
                    print("  Windows: .\\spacyenv\\Scripts\\activate")
                    print("  Linux/Mac: source spacyenv/bin/activate")
                    return 0
    
    return 1

if __name__ == "__main__":
    sys.exit(main())

