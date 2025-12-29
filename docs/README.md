# No-Borders KVM Switch - Documentation

## Overview

The No-Borders KVM Switch is a cross-platform application that allows seamless keyboard and mouse sharing between multiple computers over a network connection. This tool eliminates the need for physical KVM switches and enables smooth workflow across different machines.

## Architecture

### Project Structure

```
no-borders-kvm/
├── src/kvm_switch/           # Main package
│   ├── core/                 # Core functionality
│   │   ├── kvm_switch.py     # Main application class
│   │   └── network.py        # Network communication
│   ├── ui/                   # User interface components
│   │   ├── splash.py         # Splash screen
│   │   ├── control_panel.py  # Main control UI
│   │   └── overlay.py        # Server overlay
│   ├── handlers/             # Event handlers
│   │   ├── input_handler.py  # Input capture/simulation
│   │   └── message_handler.py # Message processing
│   └── utils/                # Utilities
│       ├── config.py         # Configuration constants
│       └── setup.py          # Auto-dependency setup
├── scripts/                  # Build and utility scripts
├── tests/                    # Test suite
└── docs/                     # Documentation
```

### Components

#### Core Components

- **KVMSwitch**: Main application coordinator
- **NetworkManager**: Handles peer discovery and communication
- **InputHandler**: Manages input capture and simulation
- **MessageHandler**: Processes incoming messages

#### UI Components

- **SplashScreen**: Animated brand splash screen
- **ControlPanel**: Main control interface
- **ServerOverlay**: Fullscreen overlay for server

#### Utilities

- **Configuration**: Centralized settings and constants
- **Auto-setup**: Automatic dependency installation

## Communication Protocol

### Discovery Phase

1. Server broadcasts presence using UDP on port 54321
2. Client listens for broadcasts and shows approval dialog
3. Client approves connection to specific server

### Connection Phase

1. TCP connection established on port 54322
2. Screen dimensions exchanged
3. Initial control state set (server has control)

### Message Types

- `control_request`: Request control from peer
- `control_release`: Release control to peer
- `mouse_move`: Mouse movement data
- `mouse_click`: Mouse button events
- `mouse_scroll`: Mouse scroll events
- `key`: Keyboard events

## Control Flow

### Server Mode
- Initially has control of both systems
- Can give control to client by clicking button
- Shows overlay when client has control
- Receives input events and forwards to client

### Client Mode
- Initially controlled by server
- Receives control when server gives it
- Can return control to server by clicking button
- Executes received input commands

## Configuration

All configuration is centralized in `utils/config.py`:

- Network ports and intervals
- UI dimensions and colors
- Default screen dimensions
- Required dependencies

## Testing

The project includes comprehensive test coverage:

- Network functionality tests
- Input/message handler tests
- UI component tests
- Integration tests

Run tests with:
```bash
python -m pytest tests/
```

## Development

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to all public methods
- Maintain modular architecture

### Adding Features
1. Determine appropriate module for new functionality
2. Add necessary configuration to `config.py`
3. Implement feature with proper error handling
4. Add comprehensive tests
5. Update documentation

### Build Process
1. Clean previous builds: `./scripts/clean.sh`
2. Build package: `./scripts/build.sh`
3. Install for development: `./scripts/install.sh`
4. Run application: `./scripts/run.sh`