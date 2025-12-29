"""
Auto-setup functionality for dependency installation
"""

import subprocess
import sys
import os
from typing import List
from .config import REQUIRED_PACKAGES

def setup_environment() -> None:
    """
    Automatically install dependencies if needed
    
    This function checks for required packages and installs them
    if they're not available, using various fallback methods.
    """
    # Check if pynput is already installed
    try:
        import pynput
        return  # Already installed, skip setup
    except ImportError:
        pass
    
    print("📦 Installing dependencies...")
    
    python_exe = sys.executable
    
    # Try different installation methods
    install_commands = [
        # Method 1: User install (no sudo needed)
        [python_exe, "-m", "pip", "install", "--user"] + REQUIRED_PACKAGES,
        # Method 2: Break system packages (Debian/Ubuntu externally-managed)
        [python_exe, "-m", "pip", "install", "--break-system-packages"] + REQUIRED_PACKAGES,
        # Method 3: Use pip3 directly
        ["pip3", "install", "--user"] + REQUIRED_PACKAGES,
    ]
    
    installed = False
    for cmd in install_commands:
        try:
            subprocess.check_call(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            installed = True
            print("✅ Dependencies installed successfully!")
            break
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    if not installed:
        print("\n❌ Could not install dependencies automatically.")
        print("Please run manually: pip3 install --user pynput")
        sys.exit(1)
    
    # Restart the script to use newly installed package
    print("🔄 Restarting...")
    os.execv(python_exe, [python_exe] + sys.argv)

def check_dependencies() -> bool:
    """
    Check if all required dependencies are available
    
    Returns:
        bool: True if all dependencies are available, False otherwise
    """
    try:
        import pynput
        return True
    except ImportError:
        return False

def install_package(package: str) -> bool:
    """
    Install a specific package
    
    Args:
        package: Package specification (e.g., "pynput==1.7.6")
        
    Returns:
        bool: True if installation was successful, False otherwise
    """
    python_exe = sys.executable
    
    install_commands = [
        [python_exe, "-m", "pip", "install", "--user", package],
        [python_exe, "-m", "pip", "install", "--break-system-packages", package],
        ["pip3", "install", "--user", package],
    ]
    
    for cmd in install_commands:
        try:
            subprocess.check_call(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    return False