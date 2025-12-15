#!/usr/bin/env python3
"""
KVM Share - Mouse and Keyboard sharing across computers
Similar to Barrier/Synergy - Share mouse/keyboard between 2-3 computers
Production-ready version with complete error handling
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
from pathlib import Path

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "kvm_config.json")
VENV_DIR = os.path.join(SCRIPT_DIR, "kvm_venv")
PORT = 24800
BUFFER_SIZE = 4096
VERSION = "1.0.0"

def get_platform():
    """Detect operating system"""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    else:
        return "unsupported"

def print_header():
    """Print application header"""
    print("\n" + "="*60)
    print(f"KVM Share v{VERSION}")
    print("Mouse & Keyboard Sharing Tool")
    print("="*60)

def install_system_dependencies_linux():
    """Install system dependencies on Linux"""
    print("\n→ Installing system dependencies (Linux)...")
    
    try:
        # Update package list
        subprocess.run(["sudo", "apt", "update"], check=False, capture_output=True, timeout=60)
        
        # Fix any broken packages
        subprocess.run(["sudo", "apt", "--fix-broken", "install", "-y"], check=False, capture_output=True, timeout=60)
        
        # Try version-specific packages first (e.g., python3.10-venv)
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        version_specific = [
            f"python{python_version}-venv",
            f"python{python_version}-dev"
        ]
        
        generic_packages = ["python3-tk", "gcc", "build-essential"]
        
        # Try version-specific first
        result = subprocess.run(
            ["sudo", "apt", "install", "-y"] + version_specific + generic_packages,
            check=False,
            capture_output=True,
            timeout=300
        )
        
        if result.returncode != 0:
            # Fall back to generic python3-venv and python3-dev
            print("→ Trying generic packages...")
            result = subprocess.run(
                ["sudo", "apt", "install", "-y", "python3-venv", "python3-dev"] + generic_packages,
                check=False,
                capture_output=True,
                timeout=300
            )
        
        # Check if critical packages are available
        has_dev = subprocess.run(["which", "gcc"], capture_output=True, timeout=5).returncode == 0
        
        if has_dev:
            print("✓ System dependencies ready!")
            return True
        
        print("⚠ Some dependencies may be missing, but continuing...")
        return True
        
    except subprocess.TimeoutExpired:
        print("✗ Installation timed out")
        return False
    except Exception as e:
        print(f"✗ Error during installation: {e}")
        return False

def check_dependencies_installed():
    """Check if Python dependencies are already installed"""
    try:
        import pynput
        from PIL import Image
        return True
    except ImportError:
        return False

def setup_environment():
    """Setup virtual environment or install packages globally"""
    system = get_platform()
    
    # If dependencies are already available, skip setup
    if check_dependencies_installed():
        print("✓ Dependencies already installed!")
        return True
    
    print("\n→ Setting up Python environment...")
    
    # On Linux, try to install system dependencies first
    if system == "linux" and not os.path.exists(VENV_DIR):
        if not install_system_dependencies_linux():
            print("⚠ System dependencies installation had issues")
    
    # Try to create venv
    if not os.path.exists(VENV_DIR):
        print("→ Creating virtual environment...")
        try:
            # Try with --copies for compatibility
            result = subprocess.run(
                [sys.executable, "-m", "venv", "--copies", VENV_DIR],
                check=False,
                capture_output=True,
                timeout=60
            )
            
            if result.returncode != 0:
                # Try without --copies
                result = subprocess.run(
                    [sys.executable, "-m", "venv", VENV_DIR],
                    check=False,
                    capture_output=True,
                    timeout=60
                )
            
            if result.returncode == 0:
                print("✓ Virtual environment created")
            else:
                raise Exception("Venv creation failed")
                
        except Exception as e:
            print(f"✗ Virtual environment creation failed: {e}")
            print("→ Falling back to user installation...")
            return install_to_user()
    
    # Install packages in venv
    if system == "windows":
        pip_path = os.path.join(VENV_DIR, "Scripts", "pip.exe")
        python_path = os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:
        pip_path = os.path.join(VENV_DIR, "bin", "pip")
        python_path = os.path.join(VENV_DIR, "bin", "python")
    
    print("→ Installing Python packages...")
    try:
        # Install packages directly without pip upgrade
        result = subprocess.run(
            [pip_path, "install", "pynput", "Pillow"],
            capture_output=True,
            timeout=300,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Python packages installed!")
            return python_path
        else:
            # Try without capture for better visibility
            print("→ Retrying installation...")
            result = subprocess.run(
                [pip_path, "install", "pynput", "Pillow"],
                timeout=300
            )
            if result.returncode == 0:
                print("✓ Python packages installed!")
                return python_path
            raise Exception("Package installation failed")
            
    except subprocess.TimeoutExpired:
        print("✗ Installation timed out")
        print("→ Falling back to user installation...")
        return install_to_user()
    except Exception as e:
        print(f"✗ Package installation failed: {e}")
        print("→ Falling back to user installation...")
        return install_to_user()

def install_to_user():
    """Install packages to user directory as fallback"""
    print("\n→ Installing to user directory (no venv)...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--user", "pynput", "Pillow"],
            timeout=300
        )
        
        if result.returncode == 0:
            print("✓ Packages installed to user directory!")
            return None  # Signal to continue without venv
        else:
            print("\n✗ Installation failed")
            print("\nPlease install manually:")
            print("  pip install --user pynput Pillow")
            print("\nOr on Linux:")
            print("  sudo apt install python3-pip")
            print("  pip3 install --user pynput Pillow")
            sys.exit(1)
            
    except subprocess.TimeoutExpired:
        print("✗ Installation timed out")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Installation error: {e}")
        sys.exit(1)

def cleanup():
    """Delete virtual environment and config"""
    print("\n→ Cleaning up...")
    
    removed = []
    
    # Remove venv
    if os.path.exists(VENV_DIR):
        try:
            shutil.rmtree(VENV_DIR)
            removed.append("Virtual environment")
        except Exception as e:
            print(f"✗ Failed to remove venv: {e}")
    
    # Remove config
    if os.path.exists(CONFIG_FILE):
        try:
            os.remove(CONFIG_FILE)
            removed.append("Configuration file")
        except Exception as e:
            print(f"✗ Failed to remove config: {e}")
    
    if removed:
        print(f"✓ Removed: {', '.join(removed)}")
    else:
        print("→ Nothing to clean up")
    
    print("Cleanup complete!")

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
        self.screen_width = 1920
        self.screen_height = 1080
        
        # Get actual screen dimensions
        try:
            system = get_platform()
            if system == "linux":
                import tkinter as tk
                root = tk.Tk()
                self.screen_width = root.winfo_screenwidth()
                self.screen_height = root.winfo_screenheight()
                root.destroy()
            elif system == "windows":
                import ctypes
                user32 = ctypes.windll.user32
                self.screen_width = user32.GetSystemMetrics(0)
                self.screen_height = user32.GetSystemMetrics(1)
        except:
            pass
    
    def start(self):
        """Start the server"""
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind(("0.0.0.0", self.port))
            self.server_socket.listen(2)
        except OSError as e:
            print(f"\n✗ Failed to start server: {e}")
            print(f"Port {self.port} may already be in use.")
            return
        
        ip = get_local_ip()
        print(f"\n{'='*60}")
        print(f"SERVER STARTED")
        print(f"{'='*60}")
        print(f"IP Address: {ip}:{self.port}")
        print(f"Screen: {self.screen_width}x{self.screen_height}")
        print(f"\nWaiting for clients...")
        print(f"Press Ctrl+C to stop")
        print(f"{'='*60}\n")
        
        # Start accepting clients
        threading.Thread(target=self.accept_clients, daemon=True).start()
        
        # Start mouse/keyboard capture
        try:
            self.capture_input()
        except KeyboardInterrupt:
            self.stop()
    
    def accept_clients(self):
        """Accept client connections"""
        while self.running:
            try:
                self.server_socket.settimeout(1.0)
                try:
                    client_socket, addr = self.server_socket.accept()
                except socket.timeout:
                    continue
                
                if len(self.clients) >= 2:
                    client_socket.send(b"ERROR:MAX_CLIENTS")
                    client_socket.close()
                    continue
                
                # Receive client info
                client_socket.settimeout(5.0)
                data = client_socket.recv(BUFFER_SIZE).decode()
                client_info = json.loads(data)
                
                position = client_info.get("position", "right")
                self.client_positions[client_socket] = position
                self.clients.append(client_socket)
                
                print(f"✓ Client connected: {addr[0]} ({position})")
                print(f"  Active clients: {len(self.clients)}/2\n")
                
                # Send acknowledgment
                response = json.dumps({
                    "status": "connected",
                    "server_screen": {"width": self.screen_width, "height": self.screen_height}
                })
                client_socket.send(response.encode())
                client_socket.settimeout(None)
                
                # Handle client in separate thread
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
                
            except Exception as e:
                if self.running:
                    pass  # Silently ignore connection errors
    
    def handle_client(self, client_socket):
        """Handle individual client connection"""
        try:
            while self.running:
                client_socket.settimeout(1.0)
                try:
                    data = client_socket.recv(BUFFER_SIZE)
                    if not data:
                        break
                    
                    # Check for "return to server" message
                    try:
                        msg = json.loads(data.decode())
                        if msg.get("type") == "return_to_server":
                            self.current_screen = "server"
                            self.active_client = None
                            print("← Returned to server")
                    except:
                        pass
                except socket.timeout:
                    continue
                    
        except:
            pass
        finally:
            if client_socket in self.clients:
                self.clients.remove(client_socket)
                if client_socket in self.client_positions:
                    del self.client_positions[client_socket]
            try:
                client_socket.close()
            except:
                pass
            print(f"✗ Client disconnected. Active: {len(self.clients)}/2")
    
    def capture_input(self):
        """Capture mouse and keyboard input"""
        from pynput import mouse, keyboard
        
        def on_move(x, y):
            if self.current_screen == "server":
                # Check if mouse moved to edge
                if x >= self.screen_width - 1:
                    self.switch_to_client("right", 0, y)
                elif x <= 0:
                    self.switch_to_client("left", self.screen_width - 1, y)
            else:
                # Send mouse movement to active client
                self.send_to_active_client({
                    "type": "mouse_move",
                    "x": x,
                    "y": y
                })
        
        def on_click(x, y, button, pressed):
            if self.current_screen != "server":
                self.send_to_active_client({
                    "type": "mouse_click",
                    "x": x,
                    "y": y,
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
            if self.current_screen != "server":
                try:
                    key_str = str(key).replace("'", "")
                    self.send_to_active_client({
                        "type": "key_press",
                        "key": key_str
                    })
                except:
                    pass
        
        def on_release(key):
            if self.current_screen != "server":
                try:
                    key_str = str(key).replace("'", "")
                    self.send_to_active_client({
                        "type": "key_release",
                        "key": key_str
                    })
                except:
                    pass
        
        # Start listeners
        mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
        keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        
        mouse_listener.start()
        keyboard_listener.start()
        
        print("✓ Input capture active")
        print("→ Move mouse to screen edge to switch\n")
        
        mouse_listener.join()
        keyboard_listener.join()
    
    def switch_to_client(self, position, x, y):
        """Switch control to a client"""
        for client_socket, client_pos in self.client_positions.items():
            if client_pos == position:
                self.current_screen = position
                self.active_client = client_socket
                print(f"→ Switched to {position} client")
                
                # Send switch command
                self.send_to_active_client({
                    "type": "switch",
                    "x": x,
                    "y": y
                })
                return
    
    def send_to_active_client(self, data):
        """Send data to active client"""
        if self.active_client and self.active_client in self.clients:
            try:
                self.active_client.send(json.dumps(data).encode())
            except:
                pass
    
    def stop(self):
        """Stop the server"""
        print("\n\n→ Shutting down server...")
        self.running = False
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        print("✓ Server stopped")

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
        
        # Get screen dimensions
        try:
            system = get_platform()
            if system == "linux":
                import tkinter as tk
                root = tk.Tk()
                self.screen_width = root.winfo_screenwidth()
                self.screen_height = root.winfo_screenheight()
                root.destroy()
            elif system == "windows":
                import ctypes
                user32 = ctypes.windll.user32
                self.screen_width = user32.GetSystemMetrics(0)
                self.screen_height = user32.GetSystemMetrics(1)
        except:
            pass
    
    def connect(self):
        """Connect to server"""
        print(f"\n{'='*60}")
        print(f"CONNECTING TO SERVER")
        print(f"{'='*60}")
        print(f"Server: {self.server_ip}:{self.port}")
        print(f"Position: {self.position}")
        print(f"Screen: {self.screen_width}x{self.screen_height}")
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10.0)
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
                print(f"✓ Connected successfully!")
                print(f"\nWaiting for control...")
                print(f"Press Ctrl+C to disconnect")
                print(f"{'='*60}\n")
                self.socket.settimeout(None)
                self.running = True
                self.receive_commands()
            else:
                print(f"✗ Connection failed: {response}")
                
        except socket.timeout:
            print("\n✗ Connection timed out")
            print("Check server IP and ensure server is running")
        except ConnectionRefusedError:
            print("\n✗ Connection refused")
            print("Ensure server is running and firewall allows connections")
        except Exception as e:
            print(f"\n✗ Connection error: {e}")
    
    def receive_commands(self):
        """Receive and execute commands from server"""
        from pynput.mouse import Button
        from pynput.keyboard import Key, KeyCode
        
        while self.running:
            try:
                self.socket.settimeout(1.0)
                try:
                    data = self.socket.recv(BUFFER_SIZE)
                    if not data:
                        break
                except socket.timeout:
                    continue
                
                cmd = json.loads(data.decode())
                cmd_type = cmd.get("type")
                
                if cmd_type == "switch":
                    print("→ Control active on this computer")
                    x, y = cmd.get("x", 0), cmd.get("y", self.screen_height // 2)
                    self.mouse_controller.position = (x, y)
                
                elif cmd_type == "mouse_move":
                    x, y = cmd.get("x"), cmd.get("y")
                    
                    # Check if mouse moved to edge to return to server
                    if (self.position == "right" and x >= self.screen_width - 1) or \
                       (self.position == "left" and x <= 0):
                        # Return control to server
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
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"✗ Error: {e}")
                break
        
        print("\n✗ Disconnected from server")
    
    def handle_key(self, key_str, is_press):
        """Handle keyboard events"""
        try:
            from pynput.keyboard import Key, KeyCode
            
            # Map special keys
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
                "Key.delete": Key.delete,
                "Key.home": Key.home,
                "Key.end": Key.end,
                "Key.page_up": Key.page_up,
                "Key.page_down": Key.page_down,
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
            try:
                self.socket.close()
            except:
                pass

def main_menu():
    """Main menu interface"""
    print_header()
    
    print("\n1. Run as Server (share your mouse/keyboard)")
    print("2. Run as Client (receive control)")
    print("3. Cleanup (remove venv and config)")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        # Server mode
        server = KVMServer()
        try:
            server.start()
        except KeyboardInterrupt:
            server.stop()
    
    elif choice == "2":
        # Client mode
        print("\n" + "-"*60)
        server_ip = input("Enter server IP address: ").strip()
        if not server_ip:
            print("✗ Invalid IP address")
            return
        
        print("\nClient position:")
        print("  1. Right of server (move mouse RIGHT to switch)")
        print("  2. Left of server (move mouse LEFT to switch)")
        pos_choice = input("Select (1-2): ").strip()
        
        position = "right" if pos_choice == "1" else "left"
        
        client = KVMClient(server_ip, position)
        try:
            client.connect()
        except KeyboardInterrupt:
            print("\n\n→ Disconnecting...")
            client.stop()
    
    elif choice == "3":
        # Cleanup
        confirm = input("\nDelete all KVM data? (yes/no): ").strip().lower()
        if confirm == "yes":
            cleanup()
        else:
            print("Cancelled")
    
    elif choice == "4":
        print("\nGoodbye!")
        sys.exit(0)
    
    else:
        print("\n✗ Invalid option")

def main():
    """Main entry point"""
    system = get_platform()
    
    if system == "unsupported":
        print("✗ Unsupported OS. Only Windows and Linux are supported.")
        sys.exit(1)
    
    print(f"Detected OS: {system.upper()}")
    
    # Check if running in venv
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if not in_venv and not check_dependencies_installed():
        # Need to setup environment
        result = setup_environment()
        
        if result and isinstance(result, str):
            # Venv created successfully, restart in venv
            print("\n✓ Setup complete! Restarting...\n")
            time.sleep(1)
            os.execv(result, [result, __file__])
        elif result is None:
            # Installed to user, continue
            print("\n✓ Setup complete!\n")
            time.sleep(1)
        else:
            sys.exit(1)
    
    # Run main menu loop
    try:
        while True:
            main_menu()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
