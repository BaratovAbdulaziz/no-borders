# No-Borders KVM Switch

> **Connect Without Limits** - Cross-platform keyboard and mouse sharing tool

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows%20|%20Linux%20|%20macOS-lightgrey.svg)]()

The No-Borders KVM Switch is a professional, cross-platform application that enables seamless keyboard and mouse sharing between multiple computers over a network connection. Share your input devices without physical KVM switches or cables.

## ✨ Features

- **🔗 Seamless Sharing**: Share keyboard and mouse between multiple computers
- **🌐 Cross-Platform**: Works on Windows, Linux, and macOS
- **🚀 Auto-Setup**: Automatically installs dependencies if needed
- **💫 Beautiful UI**: Animated splash screen and intuitive control panel
- **🔒 Secure Connection**: Direct peer-to-peer network communication
- **⚡ Low Latency**: Optimized for responsive real-time control
- **🎯 Easy Setup**: Simple server/client role selection
- **🔄 Quick Toggle**: Switch control between computers with one click

## 🚀 Quick Start

### Installation

1. **Clone or download the project**:
   ```bash
   git clone https://github.com/no-borders/kvm-switch.git
   cd no-borders-kvm
   ```

2. **Install dependencies** (automatic):
   ```bash
   ./scripts/install.sh
   ```

3. **Run the application**:
   ```bash
   ./scripts/run.sh
   ```

### Alternative Installation Methods

**Using pip (recommended for development)**:
```bash
pip install -e .
kvm-switch
```

**Direct Python execution**:
```bash
python -m kvm_switch
```

## 💻 Usage

### Step 1: Choose Your Role

When you start the application, select your role:

- **Server (Controller)**: The computer that initially controls both systems
- **Client (Controlled)**: The computer that will be controlled remotely

### Step 2: Connect

1. Start the **Server** application first
2. Start the **Client** application on the second computer
3. The client will automatically detect the server and ask for approval
4. Click **Yes** to establish the connection

### Step 3: Share Control

- **Green Button**: You have control of both systems
- **Red Button**: The other computer has control
- **Click the button** to toggle control between computers

## 🛠️ Development

### Project Structure

```
no-borders-kvm/
├── src/kvm_switch/           # Main package
│   ├── core/                 # Core functionality
│   ├── ui/                   # User interface
│   ├── handlers/             # Event handlers
│   └── utils/                # Utilities
├── scripts/                  # Build scripts
├── tests/                    # Test suite
└── docs/                     # Documentation
```

### Build Scripts

- **`./scripts/clean.sh`**: Clean build artifacts
- **`./scripts/build.sh`**: Build distribution packages
- **`./scripts/install.sh`**: Install dependencies and package
- **`./scripts/run.sh`**: Run the application

### Development Setup

1. **Create virtual environment**:
   ```bash
   ./scripts/install.sh --venv
   ```

2. **Activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```

3. **Run in development mode**:
   ```bash
   python -m kvm_switch
   ```

### Running Tests

```bash
# Install test dependencies
pip install -e .[test]

# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=kvm_switch --cov-report=html
```

## 📋 Requirements

### System Requirements

- **Python**: 3.7 or higher
- **Operating System**: Windows, Linux, or macOS
- **Network**: Both computers must be on the same network

### Dependencies

- `pynput>=1.7.6`: For keyboard and mouse input handling

Dependencies are automatically installed when you run the application for the first time.

## 🔧 Configuration

The application uses sensible defaults, but you can customize settings in `src/kvm_switch/utils/config.py`:

```python
# Network settings
BROADCAST_PORT = 54321
COMM_PORT = 54322
BROADCAST_INTERVAL = 2

# UI settings
CONTROL_PANEL_WIDTH = 200
CONTROL_PANEL_HEIGHT = 80

# Screen dimensions (auto-detected)
DEFAULT_SCREEN_WIDTH = 1920
DEFAULT_SCREEN_HEIGHT = 1080
```

## 🎯 How It Works

1. **Discovery**: Server broadcasts its presence on the network
2. **Connection**: Client detects server and establishes secure TCP connection
3. **Synchronization**: Both computers exchange screen dimensions
4. **Control**: Input events are captured and transmitted between computers
5. **Switching**: Control can be toggled seamlessly between machines

## 🔒 Security

- Direct peer-to-peer communication (no external servers)
- Connection approval required on client side
- Traffic stays within your local network
- No data is stored or transmitted to external services

## 🐛 Troubleshooting

### Common Issues

**Connection Failed**:
- Ensure both computers are on the same network
- Check firewall settings (ports 54321 and 54322)
- Try running as administrator/sudo if needed

**Dependencies Not Installing**:
```bash
# Manual installation
pip3 install --user pynput==1.7.6

# Or with system packages flag
pip3 install --break-system-packages pynput==1.7.6
```

**Permission Errors**:
- On macOS: Enable accessibility permissions for Terminal/Python
- On Linux: You may need to run with appropriate permissions

### Getting Help

1. Check the [documentation](docs/)
2. Look at [existing issues](https://github.com/no-borders/kvm-switch/issues)
3. Create a new issue with detailed information

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Python and Tkinter
- Uses `pynput` for cross-platform input handling
- Inspired by professional KVM switch solutions

---

**No-Borders KVM Switch** - Connecting computers, eliminating boundaries.

For more information, visit our [documentation](docs/) or check out the [project wiki](https://github.com/no-borders/kvm-switch/wiki).