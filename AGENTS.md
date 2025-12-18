# AGENTS.md

## Build/Lint/Test Commands
- **Build**: None (pure Python script, runs directly)
- **Lint**: None configured; optionally `flake8 KVM.py` or `python -m py_compile KVM.py`
- **Test**: Manual testing only via `python KVM.py`
- **Single Test**: N/A (no automated tests; test features manually through the interactive menu)
- **Dependencies**: `pynput`, `Pillow`, `keyboard` (auto-installed in virtual environment)

## Code Style Guidelines
- **Imports**: Standard library first, then third-party; group with blank lines between groups
- **Formatting**: 4-space indentation; no strict line length limit; minimal blank lines
- **Types**: No type hints; dynamic typing throughout
- **Naming**: snake_case for functions/variables, PascalCase for classes, UPPER_CASE for constants
- **Error Handling**: Broad try/except blocks with print-based logging; no custom exceptions
- **Docstrings**: Required for all functions and classes; use triple quotes
- **Comments**: Sparse and minimal; prefer self-documenting code
- **Structure**: Modular design with classes for Server/Client; main() entry point
- **Platform**: Cross-platform (Linux/Windows) with OS detection and conditional code
- **Dependencies**: Import heavy libraries only when needed; graceful fallbacks for missing deps