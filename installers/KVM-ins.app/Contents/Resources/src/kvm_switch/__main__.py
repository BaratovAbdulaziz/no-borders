"""
Main entry point for No-Borders KVM Switch
Run with: python -m kvm_switch
"""

import sys
import traceback

from .utils.setup import setup_environment
from .core.kvm_switch import KVMSwitch


def main() -> None:
    """Main entry point"""
    # Setup environment and dependencies
    setup_environment()
    
    # Create and run KVM switch application
    app = KVMSwitch()
    
    try:
        app.start()
    except KeyboardInterrupt:
        print("\nShutdown requested")
        app.cleanup()
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
        app.cleanup()


if __name__ == "__main__":
    main()