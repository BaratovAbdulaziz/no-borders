"""
Configuration constants for No-Borders KVM Switch
"""
from typing import Final

# Network configuration
BROADCAST_PORT: Final[int] = 54321
COMM_PORT: Final[int] = 54322
MAGIC_MESSAGE: Final[bytes] = b"NO_BORDERS_V0.2.1"

# Application configuration
APP_NAME: Final[str] = "No-Borders"
APP_VERSION: Final[str] = "0.2.1"
LICENSE: Final[str] = "MIT"

# Screen configuration (defaults)
DEFAULT_SCREEN_WIDTH: Final[int] = 1920
DEFAULT_SCREEN_HEIGHT: Final[int] = 1080

# UI configuration
SPLASH_WIDTH: Final[int] = 500
SPLASH_HEIGHT: Final[int] = 300
SETUP_WIDTH: Final[int] = 550
SETUP_HEIGHT: Final[int] = 850
INDICATOR_WIDTH: Final[int] = 220
INDICATOR_HEIGHT: Final[int] = 100

# Connection timeouts
CONNECTION_TIMEOUT: Final[float] = 10.0
SERVER_TIMEOUT: Final[float] = 30.0
MESSAGE_TIMEOUT: Final[float] = 1.0
RECONNECT_DELAY: Final[float] = 3.0

# Update intervals
BROADCAST_INTERVAL: Final[float] = 1.0
INDICATOR_UPDATE_INTERVAL: Final[float] = 0.3
DISCOVERY_TIMEOUT: Final[float] = 1.0

# Dependencies
PYNPUT_VERSION: Final[str] = "1.7.6"