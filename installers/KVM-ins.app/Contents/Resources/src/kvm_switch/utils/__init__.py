"""
Utility modules for No-Borders KVM Switch
"""

from .config import *
from .setup import setup_environment, check_dependencies, create_virtual_environment

__all__ = [
    'setup_environment',
    'check_dependencies', 
    'create_virtual_environment',
    'APP_NAME',
    'APP_VERSION',
    'LICENSE',
    'BROADCAST_PORT',
    'COMM_PORT',
    'MAGIC_MESSAGE',
    'DEFAULT_SCREEN_WIDTH',
    'DEFAULT_SCREEN_HEIGHT',
    'SPLASH_WIDTH',
    'SPLASH_HEIGHT',
    'SETUP_WIDTH',
    'SETUP_HEIGHT',
    'INDICATOR_WIDTH',
    'INDICATOR_HEIGHT',
    'CONNECTION_TIMEOUT',
    'SERVER_TIMEOUT',
    'MESSAGE_TIMEOUT',
    'RECONNECT_DELAY',
    'BROADCAST_INTERVAL',
    'INDICATOR_UPDATE_INTERVAL',
    'DISCOVERY_TIMEOUT',
    'PYNPUT_VERSION'
]