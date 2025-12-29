"""
Configuration constants and settings for the KVM Switch application
"""

# Network configuration
BROADCAST_PORT = 54321
COMM_PORT = 54322
BROADCAST_INTERVAL = 2
MAGIC_MESSAGE = b"KVM_SWITCH_DISCOVERY"

# UI configuration
SPLASH_DURATION = 3000  # milliseconds
SPLASH_WIDTH = 600
SPLASH_HEIGHT = 400

CONTROL_PANEL_WIDTH = 200
CONTROL_PANEL_HEIGHT = 80

# Default screen dimensions
DEFAULT_SCREEN_WIDTH = 1920
DEFAULT_SCREEN_HEIGHT = 1080

# Colors
UI_COLORS = {
    'connected': 'green',
    'disconnected': 'gray',
    'no_control': 'red',
    'splash_bg': '#1a1a1a',
    'splash_border': '#00a8ff',
    'splash_text': '#ffffff',
    'splash_tagline': '#888888'
}

# Fonts
FONTS = {
    'splash_title': ("Arial", 48, "bold"),
    'splash_tagline': ("Arial", 16),
    'control_button': ("Arial", 10, "bold"),
    'overlay_text': ("Arial", 24)
}

# Dependencies
REQUIRED_PACKAGES = [
    "pynput==1.7.6"
]

# Application metadata
APP_NAME = "No-Borders KVM Switch"
APP_DESCRIPTION = "Connect Without Limits"
APP_VERSION = "1.0.0"
APP_AUTHOR = "No-Borders"
APP_LICENSE = "MIT"