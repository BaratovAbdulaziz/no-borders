"""
No-Borders KVM Switch Tool - Connect Without Limits
Cross-platform keyboard and mouse sharing tool

Author: No-Borders
License: MIT
"""

__version__ = "1.0.0"
__author__ = "No-Borders"
__license__ = "MIT"
__description__ = "Cross-platform keyboard and mouse sharing tool"

from .core.kvm_switch import KVMSwitch

__all__ = ['KVMSwitch']