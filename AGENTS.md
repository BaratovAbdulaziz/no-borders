# AGENTS.md

## Build/Lint/Test Commands
- **Build**: None (pure Python script, runs directly)
- **Lint**: `flake8 KVM.py` or `python -m py_compile KVM.py`
- **Test**: Manual testing via `python KVM.py` (interactive menu: start server/client, test mouse/keyboard sharing)
- **Single Test**: N/A (no automated tests; manually test features through main menu)
- **Dependencies**: `pynput`, `Pillow`, `keyboard` (installed in virtual environment)
- **Python Version**: 3.7+

## Code Style Guidelines
- **Imports**: Standard library first, then third-party; blank lines between groups; conditional for platform-specific
- **Formatting**: 4-space indentation; no line length limit; minimal blank lines; consistent spacing
- **Types**: No type hints; dynamic typing; runtime checks where needed
- **Naming**: snake_case for functions/variables, PascalCase for classes, UPPER_CASE for constants/config
- **Error Handling**: Broad try/except with print logging; graceful fallbacks; no custom exceptions
- **Docstrings**: Required for functions/classes; triple quotes; concise and descriptive
- **Comments**: Sparse; self-documenting code preferred; explain complex logic only
- **Structure**: Node/Discovery/Link/InputCapture/InputInject classes; main() entry; GUI components
- **Platform**: Cross-platform (Linux/Windows); OS detection; ctypes for Windows; tkinter for GUI
- **Dependencies**: Import heavy libs when needed; fallbacks for missing deps; venv isolation
- **Threading**: Threading for network/concurrent tasks; daemon threads; proper cleanup
- **Networking**: UDP broadcast discovery; TCP JSON messaging; 1024 buffer; ports 50000/50001
- **UI/UX**: tkinter GUI with draggable button; overlay for control indication; cross-platform
- **Configuration**: Constants at top; TOKEN security; configurable ports/sizes