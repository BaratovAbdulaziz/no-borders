# No-Borders KVM Switch

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

⚡ **Seamless Multi-Computer Control**

No-Borders is a professional KVM (Keyboard, Video, Mouse) switch application that enables you to control multiple computers with a single keyboard and mouse across a network connection. Move seamlessly between machines without physical hardware switches.

## ✨ Features

- **🔄 Automatic Discovery**: No IP configuration needed - auto-discover other machines
- **🖱️ Real-time Input**: Smooth mouse and keyboard control with minimal latency
- **🎛️ Flexible Control**: Choose between button toggle or custom hotkey
- **🎨 Modern UI**: Beautiful, animated interface with professional design
- **🔒 Secure**: Direct peer-to-peer connections over your local network
- **🌐 Cross-platform**: Works on Linux, macOS, and Windows
- **⚙️ Auto-setup**: Installs dependencies automatically on first run
- **📊 Status Indicators**: Clear visual feedback for connection and control state

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/no-borders/no-borders-kvm.git
cd no-borders-kvm

# Install with auto-dependency setup
./scripts/install.sh

# Run the application
./scripts/run.sh
```

### Alternative Installation

```bash
# Using pip (user install)
pip install --user git+https://github.com/no-borders/no-borders-kvm.git

# Or download and run directly
python -m kvm_switch
```

## 📖 Usage

### Server Mode (Control other computers)

1. Launch No-Borders
2. Select **SERVER** mode
3. Choose control method:
   - **Toggle Button**: Click the indicator button to switch control
   - **Custom Hotkey**: Record a key combination (e.g., Ctrl+Shift+Space)
4. The server will broadcast and wait for clients
5. Use your chosen control method to toggle between machines

### Client Mode (Be controlled by others)

1. Launch No-Borders  
2. Select **CLIENT** mode
3. The client will auto-discover and connect to servers
4. Your keyboard and mouse will be controlled when server transfers control

## 🔧 Configuration

### Network Settings

- **Discovery Port**: 54321 (UDP broadcasts)
- **Communication Port**: 54322 (TCP connections)
- **Protocol**: Custom JSON messaging over TCP
- **Security**: Local network only, peer-to-peer

### Control Methods

| Method | Description | Use Case |
|--------|-------------|-----------|
| **Button** | Click indicator button | Quick access, visible UI |
| **Hotkey** | Custom key combo | Fast switching, no mouse needed |

### UI Features

- **Animated Splash**: Professional startup animation
- **Draggable Indicator**: Status window you can position anywhere
- **Visual Overlay**: Clear indication when control is transferred
- **Status Colors**: 
  - 🟡 Yellow: Connecting
  - 🟢 Green: In Control  
  - 🔴 Red: Peer Control

## 🏗️ Development

### Build from Source

```bash
# Clean previous builds
./scripts/clean.sh --all

# Build packages
./scripts/build.sh

# Install in development mode
./scripts/install.sh --dev
```

### Project Structure

```
src/kvm_switch/
├── core/           # Main application logic
├── ui/             # User interface components  
├── handlers/        # Input and message handling
└── utils/          # Configuration and setup
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/
```

## 🔒 Requirements

- **Python**: 3.7 or higher
- **Dependencies**: Auto-installed (pynput 1.7.6, tkinter)
- **Network**: Local network connectivity
- **Permissions**:
  - **Linux**: X11 access
  - **macOS**: Accessibility permissions  
  - **Windows**: Standard user permissions

## 🐛 Troubleshooting

### Common Issues

**"Permission denied" or "Access denied"**
- **Linux**: Run with `xhost +local:` or check X11 permissions
- **macOS**: Grant Accessibility permissions in System Preferences
- **Windows**: Run as Administrator if needed

**"No computers found"**
- Check firewall settings for ports 54321-54322
- Ensure all machines are on the same network
- Disable VPN temporarily for testing

**"Input not working"**
- Verify accessibility permissions
- Check if another input device is active
- Restart the application

### Debug Mode

```bash
# Enable detailed logging
./scripts/run.sh --debug

# Or set environment variable
export KVM_DEBUG=1
python -m kvm_switch
```

### Log Analysis

```bash
# Save logs to file
./scripts/run.sh 2>&1 | tee kvm.log

# Filter for specific issues
grep -i "error\|failed\|timeout" kvm.log
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes
4. **Add** tests for new functionality
5. **Ensure** all tests pass: `python -m pytest`
6. **Submit** a pull request

### Code Style

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Include docstrings for classes and methods
- Maintain test coverage above 80%

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **pynput** library for cross-platform input handling
- **tkinter** for the GUI framework
- **socket** programming for network communication

## 📞 Support

- **📚 Documentation**: [Full Documentation](docs/README.md)
- **🐛 Issues**: [Report Bugs](https://github.com/no-borders/no-borders-kvm/issues)
- **💬 Discussions**: [Community Forum](https://github.com/no-borders/no-borders-kvm/discussions)
- **📖 Wiki**: [Knowledge Base](https://github.com/no-borders/no-borders-kvm/wiki)

---

**⚡ No-Borders - Break down the barriers between your computers.**