# PyInstaller Configuration for No-Borders KVM
# Additional hooks and configurations for better compatibility

# pynput hook for better detection
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect pynput data files
datas = []
hiddenimports = []

# pynput specific handling
datas += collect_data_files('pynput')
hiddenimports += collect_submodules('pynput')

# Platform-specific hidden imports
import platform
import sys

if platform.system() == 'Windows':
    hiddenimports.extend([
        'pywin32',
        'win32api',
        'win32con',
        'win32gui',
        'win32process',
    ])
elif platform.system() == 'Darwin':  # macOS
    hiddenimports.extend([
        'Cocoa',
        'Quartz',
        'AppKit',
    ])
elif platform.system() == 'Linux':
    hiddenimports.extend([
        'Xlib',
        'Xlib.display',
        'Xlib.ext',
    ])

# Standard Python modules that might be missed
hiddenimports.extend([
    'threading',
    'socket',
    'json',
    'configparser',
    'pathlib',
    'asyncio',
])

# Additional data collection
try:
    from PyInstaller.utils.hooks import collect_dynamic_libs
    binaries = collect_dynamic_libs('pynput')
except:
    binaries = []