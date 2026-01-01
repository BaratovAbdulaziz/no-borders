"""
Setup utilities for No-Borders KVM Switch
Auto-installs dependencies and sets up environment
"""
import subprocess
import sys
import os
from typing import List, Optional

from ..utils.config import PYNPUT_VERSION


def setup_environment() -> None:
    """
    Auto-install dependencies and setup environment
    """
    # Check and install tkinter
    _setup_tkinter()
    
    # Check and install pynput
    _setup_pynput()


def _setup_tkinter() -> None:
    """Setup tkinter if needed"""
    try:
        import tkinter
    except ImportError:
        print("📦 Installing python3-tk...")
        try:
            if os.name == 'posix':
                subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'python3-tk'],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("✅ Installed! Restarting...")
                os.execv(sys.executable, [sys.executable] + sys.argv)
        except:
            print("❌ Install python3-tk manually")
            sys.exit(1)


def _setup_pynput() -> None:
    """Setup pynput if needed"""
    try:
        import pynput
        print("✅ pynput already installed")
        return
    except ImportError:
        pass
    
    print("📦 Installing pynput...")
    install_commands: List[List[str]] = [
        [sys.executable, "-m", "pip", "install", "--user", f"pynput=={PYNPUT_VERSION}"],
        ["pip3", "install", "--user", f"pynput=={PYNPUT_VERSION}"],
        ["pip", "install", "--user", f"pynput=={PYNPUT_VERSION}"],
    ]
    
    for cmd in install_commands:
        try:
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✅ Installed!")
            break
        except:
            continue
    else:
        print("❌ Failed to install pynput")
        sys.exit(1)
    
    print("🔄 Restarting...")
    os.execv(sys.executable, [sys.executable] + sys.argv)


def check_dependencies() -> bool:
    """Check if all dependencies are available"""
    try:
        import tkinter
        import pynput
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        return False


def create_virtual_environment(venv_path: Optional[str] = None) -> str:
    """Create a virtual environment if needed"""
    if venv_path is None:
        venv_path = os.path.join(os.getcwd(), "venv")
    
    if not os.path.exists(venv_path):
        print(f"Creating virtual environment at {venv_path}")
        subprocess.check_call([sys.executable, "-m", "venv", venv_path])
    
    return venv_path