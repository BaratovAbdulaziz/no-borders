#!/usr/bin/env python3
"""
No-Borders KVM Switch Tool - Main Entry Point
"""

import sys
from .utils.setup import setup_environment
from .core.kvm_switch import main

def run():
    """Main entry point for the application"""
    try:
        # Ensure dependencies are installed
        setup_environment()
        
        # Run the main application
        main()
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run()