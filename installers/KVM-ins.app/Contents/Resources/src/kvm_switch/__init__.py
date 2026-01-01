"""
No-Borders KVM Switch
Seamless Multi-Computer Control

A professional KVM switch tool that allows you to control multiple computers
with a single keyboard and mouse across a network connection.
"""

from .core.kvm_switch import KVMSwitch
from .utils.config import APP_NAME, APP_VERSION, LICENSE

__version__ = APP_VERSION
__author__ = "No-Borders Team"
__license__ = LICENSE
__email__ = "support@no-borders.com"

__all__ = [
    'KVMSwitch',
    'APP_NAME',
    'APP_VERSION',
    'LICENSE'
]