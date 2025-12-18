#!/usr/bin/env python3
"""
KVM Share - Mouse and Keyboard sharing across computers
Installation and Setup Script
"""

import os
import sys
import json
import socket
import threading
import subprocess
import platform
import shutil
import time
import ipaddress

# Standard library - no additional dependencies needed
try:
    from pathlib import Path
except ImportError:
    # Fallback for very old Python versions
    Path = None

# Enable colors on Windows
if platform.system() == "Windows":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        pass

# Configuration
VERSION = "1.0.0"
APP_NAME = "kvm-share"

# Handle paths safely for older Python or fallback
if Path:
    SCRIPT_DIR = Path(__file__).parent.resolve()
    CONFIG_DIR = Path.home() / ".kvm-share"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    VENV_DIR = CONFIG_DIR / "venv"
else:
    # Fallback to os.path
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    home = os.path.expanduser("~")
    CONFIG_DIR = os.path.join(home, ".kvm-share")
    CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
    VENV_DIR = os.path.join(CONFIG_DIR, "venv")

PORT = 24800
BUFFER_SIZE = 4096

# Portal configuration
PORTAL_X = 100  # Portal position X
PORTAL_Y = 100  # Portal position Y
PORTAL_WIDTH = 50  # Portal size
PORTAL_HEIGHT = 50  # Portal size
PORTAL_COLOR = "red"  # Portal color

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def print_banner():
    """Print application banner"""
    print("\n" + "="*70)
    print("  KVM SHARE - Mouse & Keyboard Sharing Tool")
    print("  Version " + VERSION)

    # Add system info
    system = get_platform()
    try:
        import platform
        os_info = f"{platform.system()} {platform.release()}"
        print(f"  OS: {os_info}")
    except:
        print(f"  OS: {system}")

    try:
        import psutil
        ram = psutil.virtual_memory()
        print(f"  RAM: {ram.total // (1024**3)}GB total, {ram.available // (1024**3)}GB free")
    except:
        print("  RAM: Info unavailable (install psutil for details)")

    print("="*70 + "\n")

def print_progress(message, status="info"):
    """Print formatted progress message"""
    symbols = {
        "info": "→",
        "success": "✓",
        "error": "✗",
        "wait": "⋯"
    }
    colors = {
        "info": "\033[94m",      # Blue
        "success": "\033[92m",   # Green
        "error": "\033[91m",     # Red
        "wait": "\033[93m"       # Yellow
    }
    reset = "\033[0m"
    
    symbol = symbols.get(status, "→")
    color = colors.get(status, "")
    
    # Use colors on supported terminals
    if sys.stdout.isatty():
        print(f"{color}{symbol}{reset} {message}")
    else:
        print(f"{symbol} {message}")

def get_platform():
    """Detect operating system"""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    else:
        return "unsupported"

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print_progress("Python 3.7+ is required", "error")
        print(f"  Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    return True

def install_system_dependencies():
    """Install system dependencies on Linux"""
    system = get_platform()
    if system != "linux":
        return True
    
    print_progress("Checking system dependencies...", "info")
    sys.stdout.flush()
    
    try:
        # Update package list
        subprocess.run(["sudo", "apt", "update"], 
                      check=False, capture_output=True, timeout=60)
        
        # Fix broken packages
        subprocess.run(["sudo", "apt", "--fix-broken", "install", "-y"], 
                      check=False, capture_output=True, timeout=60)
        
        # Install required packages
        packages = ["python3-venv", "python3-dev", "python3-tk", "gcc", "build-essential"]
        result = subprocess.run(
            ["sudo", "apt", "install", "-y"] + packages,
            check=False,
            capture_output=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print_progress("System dependencies installed", "success")
            return True
        
        # Check if critical packages exist
        has_dev = subprocess.run(["dpkg", "-l", "python3-dev"], 
                                capture_output=True).returncode == 0
        has_gcc = subprocess.run(["which", "gcc"], 
                                capture_output=True).returncode == 0
        
        if has_dev and has_gcc:
            print_progress("Critical dependencies available", "success")
            return True
        
        print_progress("Missing critical build tools", "error")
        return False
            
    except subprocess.TimeoutExpired:
        print_progress("System dependency installation timed out", "error")
        return False
    except Exception as e:
        print_progress(f"Error installing dependencies: {e}", "error")
        return False

def create_venv():
    """Create virtual environment"""
    print_progress("Creating virtual environment...", "info")
    sys.stdout.flush()
    
    # Create config directory (handle both Path and string)
    if Path and isinstance(CONFIG_DIR, Path):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    else:
        os.makedirs(CONFIG_DIR, exist_ok=True)
    
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", str(VENV_DIR)],
            check=True,
            capture_output=True,
            timeout=120
        )
        print_progress("Virtual environment created", "success")
        return True
    except subprocess.CalledProcessError as e:
        print_progress("Failed to create virtual environment", "error")
        print(f"\n  Error: {e}")
        return False
    except subprocess.TimeoutExpired:
        print_progress("Virtual environment creation timed out", "error")
        return False

def get_venv_python():
    """Get path to Python in virtual environment"""
    system = get_platform()
    if system == "windows":
        if Path:
            return VENV_DIR / "Scripts" / "python.exe"
        else:
            return os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:
        if Path:
            return VENV_DIR / "bin" / "python"
        else:
            return os.path.join(VENV_DIR, "bin", "python")

def get_venv_pip():
    """Get path to pip in virtual environment"""
    system = get_platform()
    if system == "windows":
        if Path:
            return VENV_DIR / "Scripts" / "pip.exe"
        else:
            return os.path.join(VENV_DIR, "Scripts", "pip.exe")
    else:
        if Path:
            return VENV_DIR / "bin" / "pip"
        else:
            return os.path.join(VENV_DIR, "bin", "pip")

def install_dependencies():
    """Install Python dependencies"""
    print_progress("Installing Python packages...", "info")

    pip_path = get_venv_pip()
    deps = ["pynput", "Pillow", "keyboard"]
    
    try:
        # Upgrade pip first
        print_progress("Upgrading pip...", "wait")
        sys.stdout.flush()
        
        result = subprocess.run(
            [str(pip_path), "install", "--upgrade", "pip"],
            capture_output=True,
            text=True,
            timeout=180
        )
        
        if result.returncode != 0:
            print_progress("Pip upgrade failed, continuing anyway...", "info")
        
        # Install dependencies with progress
        print_progress(f"Installing {', '.join(deps)}...", "wait")
        sys.stdout.flush()
        
        result = subprocess.run(
            [str(pip_path), "install", "--default-timeout", "600", 
             "--retries", "10"] + deps,
            capture_output=True,
            text=True,
            timeout=900
        )
        
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
        
        print_progress("Python packages installed", "success")
        return True
        
    except subprocess.TimeoutExpired:
        print_progress("Installation timed out", "error")
        print("\n  Your network connection may be too slow.")
        print("  Try again later or use a different network.")
        print("\n  Or install manually:")
        print(f"    {sys.executable} -m pip install --user pynput Pillow")
        return False
        
    except subprocess.CalledProcessError as e:
        print_progress("Failed to install packages", "error")
        
        # Safe error message handling
        error_msg = ""
        if hasattr(e, 'stderr') and e.stderr:
            error_msg = str(e.stderr).lower() if isinstance(e.stderr, str) else e.stderr.decode('utf-8', errors='ignore').lower()
        elif hasattr(e, 'stdout') and e.stdout:
            error_msg = str(e.stdout).lower() if isinstance(e.stdout, str) else e.stdout.decode('utf-8', errors='ignore').lower()
        
        if error_msg and ("timeout" in error_msg or "connection" in error_msg):
            print("\n  Network connection issue detected.")
            print("  Please check your internet and try again.")
        else:
            print("\n  Installation error occurred.")
            if error_msg:
                print(f"  Error: {error_msg[:200]}")
        
        print("\n  You can try installing manually:")
        print(f"    {sys.executable} -m pip install --user pynput Pillow")
        return False
    
    except Exception as e:
        print_progress(f"Unexpected error: {e}", "error")
        print("\n  You can try installing manually:")
        print(f"    {sys.executable} -m pip install --user pynput Pillow")
        return False

def run_installation():
    """Run complete installation process"""
    clear_screen()
    print_banner()
    print("Starting installation...\n")
    
    # Check Python version
    if not check_python_version():
        return False
    
    print_progress(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected", "success")
    
    # Install system dependencies on Linux
    system = get_platform()
    if system == "linux":
        if not install_system_dependencies():
            print_progress("Continuing without system dependencies...", "info")
    
    # Create virtual environment
    venv_exists = os.path.exists(str(VENV_DIR) if Path else VENV_DIR)
    if not venv_exists:
        if not create_venv():
            return False
    else:
        print_progress("Virtual environment exists", "success")
    
    # Install Python packages
    if not install_dependencies():
        return False
    
    # Save installation marker
    marker_path = os.path.join(str(CONFIG_DIR) if Path else CONFIG_DIR, ".installed")
    with open(marker_path, 'w') as f:
        f.write(VERSION)
    
    print("\n" + "="*70)
    print_progress("Installation completed successfully!", "success")
    print("="*70 + "\n")
    
    time.sleep(1)
    return True

def is_installed():
    """Check if KVM Share is installed"""
    venv_exists = os.path.exists(str(VENV_DIR) if Path else VENV_DIR)
    marker_path = os.path.join(str(CONFIG_DIR) if Path else CONFIG_DIR, ".installed")
    marker_exists = os.path.exists(marker_path)
    return venv_exists and marker_exists

def uninstall():
    """Uninstall KVM Share - remove virtual environment and config"""
    clear_screen()
    print_banner()

    print("This will remove all KVM Share data including:")
    print("• Virtual environment")
    print("• Configuration files")
    print("• Saved settings\n")

    confirm = input("Type 'yes' to confirm uninstallation: ").strip().lower()

    if confirm != "yes":
        print("\nUninstallation cancelled.")
        time.sleep(1)
        return

    print("\n" + "-"*70)

    if not CONFIG_DIR.exists() if Path else not os.path.exists(CONFIG_DIR):
        print_progress("Nothing to uninstall - already clean", "success")
        input("\nPress Enter to continue...")
        return

    print_progress("Removing KVM Share data...", "info")

    # Try up to 5 times with delay - often unlocks files
    success = False
    for attempt in range(5):
        try:
            if Path:
                shutil.rmtree(CONFIG_DIR, ignore_errors=False)
            else:
                shutil.rmtree(CONFIG_DIR)
            success = True
            break
        except PermissionError as e:
            print_progress(f"Access denied (attempt {attempt + 1}/5). Retrying in 2 seconds...", "wait")
            print("  Tip: Close all Command Prompts/PowerShell windows and Python apps")
            time.sleep(2)
        except Exception as e:
            print_progress(f"Error removing data: {e}", "error")
            break

    if success:
        print_progress("Uninstallation complete - all data removed", "success")
    else:
        print_progress("Partial removal - some files locked", "error")
        print("\nTo fully uninstall:")
        print("  1. Close ALL Command Prompt / PowerShell windows")
        print("  2. Close any running Python programs")
        print("  3. Open Task Manager → End any 'python.exe' processes")
        print(f"  4. Manually delete the folder: {CONFIG_DIR}")
        print("  5. Try uninstall again")

    input("\nPress Enter to continue...")
def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_screen_size():
    """Get screen width and height"""
    try:
        import ctypes
        user32 = ctypes.windll.user32
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        return width, height
    except:
        pass

    try:
        import tkinter as tk
        root = tk.Tk()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        return width, height
    except:
        pass

    # Fallback
    print("\n→ Could not detect screen size automatically")
    width = input("Enter screen width (default 1920): ").strip() or 1920
    height = input("Enter screen height (default 1080): ").strip() or 1080
    return int(width), int(height)

def save_config(config):
    """Save configuration"""
    if Path and isinstance(CONFIG_DIR, Path):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    else:
        os.makedirs(CONFIG_DIR, exist_ok=True)
    
    config_path = str(CONFIG_FILE) if Path else CONFIG_FILE
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

def load_config():
    """Load configuration"""
    config_path = str(CONFIG_FILE) if Path else CONFIG_FILE
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

class KVMServer:
    """Server that shares mouse and keyboard"""
    
    def __init__(self, port=PORT):
        from pynput import mouse, keyboard
        
        self.port = port
        self.clients = []
        self.client_positions = {}
        self.running = False
        self.server_socket = None
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.current_screen = "server"
        self.active_client = None
        self.screen_width, self.screen_height = get_screen_size()
        self.ctrl_pressed = False
        self.win_pressed = False
        self.hotkey_triggered = False
        self.hotkey_thread = None
        self.portal_window = None
        self.portal_enabled = False  # Disabled due to threading issues - can be enabled later
        
        # Get actual screen dimensions
        try:
            if get_platform() == "windows":
                import ctypes
                user32 = ctypes.windll.user32
                self.screen_width = user32.GetSystemMetrics(0)
                self.screen_height = user32.GetSystemMetrics(1)
            elif get_platform() == "linux":
                if os.environ.get('DISPLAY'):
                    try:
                        import tkinter as tk
                        root = tk.Tk()
                        self.screen_width = root.winfo_screenwidth()
                        self.screen_height = root.winfo_screenheight()
                        root.destroy()
                    except:
                        pass
                else:
                    print("Warning: No display detected on server. Using default 1920x1080. Enter actual size if different.")
                    try:
                        user_input = input("Server screen width (default 1920): ").strip()
                        self.screen_width = int(user_input) if user_input and user_input.isdigit() else 1920
                        user_input = input("Server screen height (default 1080): ").strip()
                        self.screen_height = int(user_input) if user_input and user_input.isdigit() else 1080
                    except KeyboardInterrupt:
                        self.screen_width = 1920
                        self.screen_height = 1080
        except:
            pass
    
    def start(self):
        """Start the server"""
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("0.0.0.0", self.port))
        self.server_socket.listen(2)
        
        ip = get_local_ip()
        print(f"\n{'='*70}")
        print(f"  SERVER STARTED")
        print(f"{'='*70}")
        print(f"\n  IP Address: {ip}")
        print(f"  Port: {self.port}")
        print(f"  Screen: {self.screen_width}x{self.screen_height}")
        print(f"\n  Waiting for clients to connect...")
        print(f"  Press Ctrl+C to stop")
        print(f"\n{'='*70}\n")
        
        # Start accepting clients
        threading.Thread(target=self.accept_clients, daemon=True).start()

        # Start mouse/keyboard capture
        self.capture_input()
    
    def accept_clients(self):
        """Accept client connections"""
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                
                if len(self.clients) >= 2:
                    client_socket.send(b"ERROR:MAX_CLIENTS")
                    client_socket.close()
                    continue
                
                # Receive client info
                data = client_socket.recv(BUFFER_SIZE).decode()
                client_info = json.loads(data)
                
                position = client_info.get("position", "right")
                self.client_positions[client_socket] = position
                self.clients.append(client_socket)
                
                print(f"✓ Client connected from {addr[0]} (position: {position})")
                print(f"  Active clients: {len(self.clients)}/2\n")
                
                # Send acknowledgment
                response = json.dumps({
                    "status": "connected",
                    "server_screen": {"width": self.screen_width, "height": self.screen_height}
                })
                client_socket.send(response.encode())
                
                # Handle client in separate thread
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
                
            except Exception as e:
                if self.running:
                    print(f"Error accepting client: {e}")
    
    def handle_client(self, client_socket):
        """Handle individual client connection"""
        try:
            while self.running:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                
                try:
                    msg = json.loads(data.decode())
                    if msg.get("type") == "return_to_server":
                        self.current_screen = "server"
                        self.active_client = None
                        print("← Returned to server")
                except:
                    pass
                    
        except:
            pass
        finally:
            if client_socket in self.clients:
                self.clients.remove(client_socket)
                if client_socket in self.client_positions:
                    del self.client_positions[client_socket]
            client_socket.close()
            print(f"Client disconnected. Active: {len(self.clients)}/2")
    
    def capture_input(self):
        """Capture mouse and keyboard input"""
        from pynput import mouse, keyboard
        
        def on_move(x, y):
            if self.current_screen == "server":
                if x >= self.screen_width - 1:
                    self.switch_to_client("right", 0, y)
                elif x <= 0:
                    self.switch_to_client("left", self.screen_width - 1, y)
            else:
                self.send_to_active_client({
                    "type": "mouse_move",
                    "x": x / self.screen_width,
                    "y": y / self.screen_height
                })
        
        def on_click(x, y, button, pressed):
            if self.current_screen != "server":
                self.send_to_active_client({
                    "type": "mouse_click",
                    "x": x / self.screen_width,
                    "y": y / self.screen_height,
                    "button": str(button),
                    "pressed": pressed
                })
        
        def on_scroll(x, y, dx, dy):
            if self.current_screen != "server":
                self.send_to_active_client({
                    "type": "mouse_scroll",
                    "dx": dx,
                    "dy": dy
                })
        
        def on_press(key):
            # Track Ctrl key
            if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                self.ctrl_pressed = True

            # Track Win/Super key - simplified detection
            if key in (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r):
                self.win_pressed = True
            # Linux Super key variants
            try:
                if hasattr(key, 'name') and 'super' in str(key).lower():
                    self.win_pressed = True
            except:
                pass

            # HOTKEY ACTIONS - Check if both modifiers are pressed
            if self.ctrl_pressed and self.win_pressed:
                if key == keyboard.Key.left:
                    print("🔥 Hotkey detected: Ctrl+Win+Left")
                    self.switch_to_any_client("left")
                    return False  # Suppress key
                elif key == keyboard.Key.right:
                    print("🔥 Hotkey detected: Ctrl+Win+Right")
                    self.switch_to_any_client("right")
                    return False
                elif key == keyboard.Key.up:
                    print("🔥 Hotkey detected: Ctrl+Win+Up")
                    self.return_to_server()
                    return False

            # Forward other keys to client if active
            if self.current_screen != "server":
                try:
                    key_str = str(key).replace("'", "")
                    self.send_to_active_client({"type": "key_press", "key": key_str})
                except:
                    pass

        def on_release(key):
            # Reset modifier states
            if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                self.ctrl_pressed = False

            if key in (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r):
                self.win_pressed = False

            try:
                if hasattr(key, 'name') and 'super' in str(key).lower():
                    self.win_pressed = False
            except:
                pass

            # Forward key releases to client
            if self.current_screen != "server":
                try:
                    key_str = str(key).replace("'", "")
                    self.send_to_active_client({"type": "key_release", "key": key_str})
                except:
                    pass

        mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
        keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

        mouse_listener.start()
        keyboard_listener.start()

        print("✓ Input capture active")
        print("→ Move mouse to screen edge to switch to client")
        print("→ Hotkeys active: Ctrl+Super+← or → (switch to client), Ctrl+Super+↑ (back to server)")
        if self.portal_enabled:
            print(f"→ Portal active at ({PORTAL_X}, {PORTAL_Y}) - hover to switch\n")
        else:
            print()

        mouse_listener.join()
        keyboard_listener.join()
    
    def switch_to_client(self, position, x, y):
        """Switch control to a client"""
        for client_socket, client_pos in self.client_positions.items():
            if client_pos == position:
                self.current_screen = position
                self.active_client = client_socket
                print(f"→ Switched to {position} client")
                
                self.send_to_active_client({
                    "type": "switch",
                    "y": y / self.screen_height
                })
                return
    
    def send_to_active_client(self, data):
        """Send data to active client"""
        if self.active_client and self.active_client in self.clients:
            try:
                self.active_client.send(json.dumps(data).encode())
            except:
                pass

    def switch_to_right(self):
        self.switch_to_client("right", self.screen_width // 2, self.screen_height // 2)

    def switch_to_left(self):
        self.switch_to_client("left", self.screen_width // 2, self.screen_height // 2)

    def return_to_server(self):
        if self.current_screen != "server":
            # Save reference before clearing
            prev_client = self.active_client

            self.current_screen = "server"
            self.active_client = None
            print("← Returned to server via hotkey")

            # Notify the previous client
            if prev_client and prev_client in self.clients:
                try:
                    prev_client.send(json.dumps({"type": "return_to_server"}).encode())
                except:
                    pass

    def switch_to_any_client(self, direction="any"):
        """Switch to client, preferring direction if multiple"""
        if len(self.clients) == 0:
            print("No clients connected yet")
            return

        # If only one, switch to it
        if len(self.clients) == 1:
            client_socket = self.clients[0]
            position = self.client_positions[client_socket]
            self.switch_to_client(position, self.screen_width // 2, self.screen_height // 2)
            return

        # If multiple, prefer based on direction
        if direction == "portal":
            # For portal, just pick the first client
            client_socket = self.clients[0]
            position = self.client_positions[client_socket]
            self.switch_to_client(position, self.screen_width // 2, self.screen_height // 2)
            return

        preferred_pos = "left" if direction == "left" else "right"
        for client_socket, pos in self.client_positions.items():
            if pos == preferred_pos:
                self.switch_to_client(pos, self.screen_width // 2, self.screen_height // 2)
                return

        # Fallback to first if no match
        client_socket = self.clients[0]
        position = self.client_positions[client_socket]
        self.switch_to_client(position, self.screen_width // 2, self.screen_height // 2)



    def create_portal(self):
        """Create a visual portal for switching"""
        try:
            import tkinter as tk

            self.portal_window = tk.Tk()
            self.portal_window.title("KVM Portal")
            self.portal_window.geometry(f"{PORTAL_WIDTH}x{PORTAL_HEIGHT}+{PORTAL_X}+{PORTAL_Y}")
            self.portal_window.attributes("-topmost", True)  # Always on top
            self.portal_window.attributes("-alpha", 0.7)  # Semi-transparent
            self.portal_window.overrideredirect(True)  # No window borders

            # Create colored canvas
            canvas = tk.Canvas(self.portal_window, width=PORTAL_WIDTH, height=PORTAL_HEIGHT, bg=PORTAL_COLOR, highlightthickness=0)
            canvas.pack()

            # Bind mouse enter to switch
            def on_enter(event):
                self.switch_to_any_client("portal")

            canvas.bind("<Enter>", on_enter)

            # Start portal in separate thread
            def run_portal():
                self.portal_window.mainloop()

            portal_thread = threading.Thread(target=run_portal, daemon=True)
            portal_thread.start()

        except Exception as e:
            print(f"Portal creation failed: {e}")

    def stop(self):
        """Stop the server"""
        self.running = False
        for client in self.clients:
            client.close()
        if self.server_socket:
            self.server_socket.close()

        # Destroy portal window
        if self.portal_window:
            try:
                self.portal_window.destroy()
            except:
                pass

class KVMClient:
    """Client that receives mouse and keyboard control"""
    
    def __init__(self, server_ip, position="right", port=PORT):
        from pynput import mouse, keyboard
        
        self.server_ip = server_ip
        self.position = position
        self.port = port
        self.socket = None
        self.running = False
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.screen_width = 1920
        self.screen_height = 1080
        self.is_controlling = False

        # Validate IP address
        try:
            ipaddress.ip_address(self.server_ip)
        except ValueError:
            print(f"✗ Invalid IP address: {self.server_ip}")
            sys.exit(1)
        
        # Get screen dimensions
        try:
            system = get_platform()
            if system == "windows":
                import ctypes
                user32 = ctypes.windll.user32
                self.screen_width = user32.GetSystemMetrics(0)
                self.screen_height = user32.GetSystemMetrics(1)
            elif system == "linux":
                if os.environ.get('DISPLAY'):
                    try:
                        import tkinter as tk
                        root = tk.Tk()
                        self.screen_width = root.winfo_screenwidth()
                        self.screen_height = root.winfo_screenheight()
                        root.destroy()
                    except:
                        pass
                else:
                    print("Warning: No display detected on client. Using default 1920x1080. Enter actual size if different.")
                    try:
                        user_input = input("Client screen width (default 1920): ").strip()
                        self.screen_width = int(user_input) if user_input and user_input.isdigit() else 1920
                        user_input = input("Client screen height (default 1080): ").strip()
                        self.screen_height = int(user_input) if user_input and user_input.isdigit() else 1080
                    except KeyboardInterrupt:
                        self.screen_width = 1920
                        self.screen_height = 1080
        except:
            pass
    
    def connect(self):
        """Connect to server"""
        print(f"\n{'='*70}")
        print(f"  CONNECTING TO SERVER")
        print(f"{'='*70}")
        print(f"\n  Server: {self.server_ip}:{self.port}")
        print(f"  Position: {self.position}")
        print(f"  Screen: {self.screen_width}x{self.screen_height}\n")
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_ip, self.port))
        
        # Send client info
        client_info = json.dumps({
            "position": self.position,
            "screen": {"width": self.screen_width, "height": self.screen_height}
        })
        self.socket.send(client_info.encode())
        
        # Receive acknowledgment
        response = self.socket.recv(BUFFER_SIZE).decode()
        data = json.loads(response)
        
        if data.get("status") == "connected":
            print(f"{'='*70}")
            print("✓ Connected successfully!")
            print(f"{'='*70}\n")
            print("  Waiting for server to switch control...")
            print("  Press Ctrl+C to disconnect\n")
            self.running = True
            self.receive_commands()
        else:
            print(f"✗ Connection failed: {response}")
    
    def receive_commands(self):
        """Receive and execute commands from server"""
        from pynput.mouse import Button
        from pynput.keyboard import Key, KeyCode
        
        while self.running:
            try:
                data = self.socket.recv(BUFFER_SIZE)
                if not data:
                    break
                
                cmd = json.loads(data.decode())
                cmd_type = cmd.get("type")
                
                if cmd_type == "switch":
                    self.is_controlling = True
                    print("→ Control switched to this computer")
                    y = int(cmd.get("y", 0.5) * self.screen_height)
                    if self.position == "right":
                        x = 0
                    else:
                        x = self.screen_width - 1
                    self.mouse_controller.position = (x, y)
                
                elif cmd_type == "mouse_move":
                    x = int(cmd.get("x") * self.screen_width)
                    y = int(cmd.get("y") * self.screen_height)
                    
                    if (self.position == "right" and x >= self.screen_width - 1) or \
                       (self.position == "left" and x <= 0):
                        self.is_controlling = False
                        print("← Returning control to server")
                        self.socket.send(json.dumps({"type": "return_to_server"}).encode())
                    else:
                        self.mouse_controller.position = (x, y)
                
                elif cmd_type == "mouse_click":
                    button = Button.left if "left" in cmd.get("button", "").lower() else Button.right
                    if cmd.get("pressed"):
                        self.mouse_controller.press(button)
                    else:
                        self.mouse_controller.release(button)
                
                elif cmd_type == "mouse_scroll":
                    dx, dy = cmd.get("dx", 0), cmd.get("dy", 0)
                    self.mouse_controller.scroll(dx, dy)
                
                elif cmd_type == "key_press":
                    self.handle_key(cmd.get("key"), True)
                
                elif cmd_type == "key_release":
                    self.handle_key(cmd.get("key"), False)
                
            except Exception as e:
                if self.running:
                    print(f"Error: {e}")
                break
        
        print("\n✓ Disconnected from server")
    
    def handle_key(self, key_str, is_press):
        """Handle keyboard events"""
        try:
            from pynput.keyboard import Key, KeyCode
            
            key_map = {
                "Key.space": Key.space,
                "Key.enter": Key.enter,
                "Key.tab": Key.tab,
                "Key.backspace": Key.backspace,
                "Key.esc": Key.esc,
                "Key.shift": Key.shift,
                "Key.shift_r": Key.shift_r,
                "Key.ctrl": Key.ctrl,
                "Key.ctrl_r": Key.ctrl_r,
                "Key.alt": Key.alt,
                "Key.alt_r": Key.alt_r,
                "Key.up": Key.up,
                "Key.down": Key.down,
                "Key.left": Key.left,
                "Key.right": Key.right,
            }
            
            if key_str in key_map:
                key = key_map[key_str]
            elif len(key_str) == 1:
                key = key_str
            else:
                return
            
            if is_press:
                self.keyboard_controller.press(key)
            else:
                self.keyboard_controller.release(key)
        except:
            pass
    
    def stop(self):
        """Stop the client"""
        self.running = False
        if self.socket:
            self.socket.close()

def main_menu():
    """Main menu interface"""
    clear_screen()
    print_banner()
    
    print("1. Start Server (share your mouse/keyboard)")
    print("2. Connect as Client (receive control)")
    print("3. Uninstall")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        clear_screen()
        print_banner()
        server = KVMServer()
        try:
            server.start()
        except KeyboardInterrupt:
            print("\n\nShutting down server...")
            server.stop()
    
    elif choice == "2":
        clear_screen()
        print_banner()
        
        server_ip = input("Enter server IP address: ").strip()
        
        if ':' in server_ip:
            server_ip = server_ip.split(':')[0]
        
        if not server_ip:
            print("\n✗ Invalid IP address")
            input("\nPress Enter to continue...")
            return
        
        print("\nClient position:")
        print("  1. Right of server")
        print("  2. Left of server")
        pos_choice = input("\nSelect (1-2): ").strip()
        
        position = "right" if pos_choice == "1" else "left"
        
        client = KVMClient(server_ip, position)
        try:
            client.connect()
        except KeyboardInterrupt:
            print("\n\nDisconnecting...")
            client.stop()
        except Exception as e:
            print(f"\n✗ Connection error: {e}")
        
        input("\nPress Enter to continue...")
    
    elif choice == "3":
        uninstall()
        input("\nPress Enter to continue...")
    
    elif choice == "4":
        clear_screen()
        print("\nGoodbye!\n")
        sys.exit(0)
    
    else:
        print("\n✗ Invalid option")
        time.sleep(1)

def main():
    """Main entry point"""
    system = get_platform()

    if system == "unsupported":
        print("✗ Unsupported operating system")
        print("  Only Windows and Linux are supported")
        sys.exit(1)

    # Check if root access is needed for hotkeys on Linux
    if system == "linux":
        import os
        if os.geteuid() != 0:  # Not running as root
            print_progress("Hotkeys require root on Linux. Relaunching with sudo...", "info")
            try:
                import subprocess
                # Relaunch with sudo, preserving all arguments
                result = subprocess.run(['sudo', sys.executable] + sys.argv, check=True)
                sys.exit(result.returncode)  # Exit after relaunch
            except subprocess.CalledProcessError as e:
                print_progress("Failed to relaunch with sudo", "error")
                print("  Running in mouse-only mode (hotkeys disabled)")
                print("  To enable hotkeys, run: sudo python3 KVM.py")
            except KeyboardInterrupt:
                print("\nCancelled.")
                sys.exit(0)

    # Check if we're in the virtual environment
    venv_path_str = str(VENV_DIR) if Path else VENV_DIR
    if Path:
        in_venv = str(Path(sys.executable).parent.resolve()).startswith(venv_path_str)
    else:
        in_venv = os.path.dirname(os.path.abspath(sys.executable)).startswith(venv_path_str)
    
    if not in_venv:
        # Not in venv - check if installation needed
        if not is_installed():
            # Run installation
            if not run_installation():
                print("\n✗ Installation failed")
                print("  Please check the errors above and try again")
                sys.exit(1)
        
        # Launch in virtual environment
        python_path = get_venv_python()
        if Path:
            script_path = str(Path(__file__).resolve())
        else:
            script_path = os.path.abspath(__file__)
        
        print("Starting KVM Share...\n")
        time.sleep(0.5)
        
        # Convert to string and use absolute paths
        python_str = str(python_path) if Path else python_path
        os.execv(python_str, [python_str, script_path])
    
    # Running in venv - show menu
    try:
        while True:
            main_menu()
    except KeyboardInterrupt:
        clear_screen()
        print("\nGoodbye!\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
