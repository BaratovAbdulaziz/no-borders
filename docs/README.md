# No-Borders KVM Switch Documentation

## Overview

No-Borders is a professional KVM (Keyboard, Video, Mouse) switch application that enables seamless multi-computer control across a network connection. This documentation provides comprehensive information about the project architecture, usage, and development.

## Project Structure

```
no-borders-kvm/
├── src/kvm_switch/           # Main package
│   ├── __init__.py
│   ├── __main__.py           # Entry point
│   ├── core/                 # Core functionality
│   │   ├── __init__.py
│   │   ├── kvm_switch.py     # Main KVM class
│   │   └── network.py        # Network management
│   ├── ui/                   # User interface
│   │   ├── __init__.py
│   │   ├── splash.py         # Splash screen
│   │   ├── control_panel.py  # Setup dialog
│   │   └── overlay.py        # Server overlay
│   ├── handlers/              # Event handlers
│   │   ├── __init__.py
│   │   ├── input_handler.py  # Input handling
│   │   └── message_handler.py # Message processing
│   └── utils/               # Utilities
│       ├── __init__.py
│       ├── setup.py          # Environment setup
│       └── config.py         # Configuration constants
├── scripts/                 # Utility scripts
│   ├── clean.sh
│   ├── build.sh
│   ├── install.sh
│   └── run.sh
├── tests/                   # Test files
├── docs/                    # Documentation
├── requirements.txt          # Dependencies
├── setup.py                # Package setup
├── pyproject.toml          # Modern Python config
└── .gitignore             # Git ignore rules
```

## Architecture

### Core Components

1. **KVMSwitch**: Main application class that coordinates all components
2. **NetworkManager**: Handles network discovery, broadcasting, and connections
3. **UI Components**: Manages splash screen, setup dialog, and overlay
4. **Handlers**: Process input events and message communication
5. **Utils**: Provides configuration and setup utilities

### Data Flow

1. Application starts with splash screen
2. User configures mode (server/client) and control method
3. Network discovery establishes connections
4. Input handlers capture and forward events
5. Message handlers process communication
6. UI updates reflect connection status

## Installation

### Development Setup

```bash
# Clone the repository
git clone https://github.com/no-borders/no-borders-kvm.git
cd no-borders-kvm

# Install in development mode
./scripts/install.sh --dev --venv

# Run the application
./scripts/run.sh --venv
```

### Production Installation

```bash
# Install system-wide
sudo ./scripts/install.sh

# Or user-level
./scripts/install.sh

# Run directly
kvm-switch
```

## Usage

### Server Mode

1. Run the application
2. Select "SERVER" mode
3. Choose control method (Button or Hotkey)
4. Application will broadcast and wait for clients
5. Control transfers when you toggle or use hotkey

### Client Mode

1. Run the application
2. Select "CLIENT" mode
3. Application will discover and connect to servers
4. Receive input when server transfers control

## Configuration

### Network Settings

- **Broadcast Port**: 54321 (UDP)
- **Communication Port**: 54322 (TCP)
- **Magic Message**: "NO_BORDERS_V0.2.1"

### Control Methods

- **Button Mode**: Click the toggle button in the indicator
- **Hotkey Mode**: Press a custom key combination

### UI Settings

- Splash screen with fade-in animation
- Draggable status indicator
- Overlay when server loses control

## Development

### Building

```bash
# Clean previous builds
./scripts/clean.sh --all

# Build packages
./scripts/build.sh --wheel --source
```

### Testing

```bash
# Run tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_network.py
```

### Code Quality

```bash
# Check code style
flake8 src/

# Type checking
mypy src/

# Security scan
bandit -r src/
```

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure accessibility permissions on macOS/X11
2. **Network Issues**: Check firewall settings for ports 54321-54322
3. **Dependencies**: Run `./scripts/install.sh` to auto-install missing packages

### Debug Mode

```bash
# Enable debug output
./scripts/run.sh --debug

# Environment variable
export KVM_DEBUG=1
python -m kvm_switch
```

### Logs

Logs are printed to console and can be redirected:
```bash
# Save logs to file
./scripts/run.sh 2>&1 | tee kvm.log
```

## API Reference

### KVMSwitch Class

Main application class that coordinates all components.

#### Methods

- `start()`: Start the application
- `cleanup()`: Clean up resources
- `toggle_control()`: Toggle control between machines

### NetworkManager Class

Handles network discovery and connections.

#### Methods

- `start()`: Start network services
- `stop()`: Stop network services
- `start_server()`: Start server mode
- `connect_to_server(addr)`: Connect to server

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/no-borders/no-borders-kvm/issues)
- **Documentation**: [Wiki](https://github.com/no-borders/no-borders-kvm/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/no-borders/no-borders-kvm/discussions)