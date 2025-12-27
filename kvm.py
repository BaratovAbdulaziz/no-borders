#!/usr/bin/env python3
"""
KVM Switch Tool - Cross-platform keyboard and mouse sharing
Auto-setup version with dependency management
Author: Your Name
License: MIT
"""

import subprocess
import sys
import os
from pathlib import Path

# Auto-setup function
def setup_environment():
    """Automatically install dependencies if needed"""
    # Check if pynput is already installed
    try:
        import pynput
        return  # Already installed, skip setup
    except ImportError:
        pass
    
    print("📦 Installing dependencies...")
    
    # Try to install pynput
    python_exe = sys.executable
    
    # Try different installation methods
    install_commands = [
        # Method 1: User install (no sudo needed)
        [python_exe, "-m", "pip", "install", "--user", "pynput==1.7.6"],
        # Method 2: Break system packages (Debian/Ubuntu externally-managed)
        [python_exe, "-m", "pip", "install", "--break-system-packages", "pynput==1.7.6"],
        # Method 3: Use pip3 directly
        ["pip3", "install", "--user", "pynput==1.7.6"],
    ]
    
    installed = False
    for cmd in install_commands:
        try:
            subprocess.check_call(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            installed = True
            print("✅ Dependencies installed successfully!")
            break
        except:
            continue
    
    if not installed:
        print("\n❌ Could not install dependencies automatically.")
        print("Please run manually: pip3 install --user pynput")
        sys.exit(1)
    
    # Restart the script to use newly installed package
    print("🔄 Restarting...")
    os.execv(python_exe, [python_exe] + sys.argv)

# Run setup before importing other modules
setup_environment()

# Now import the rest after setup
import tkinter as tk
from tkinter import messagebox
import socket
import threading
import json
import time
import platform

# Import pynput (will be installed by setup)
from pynput import mouse, keyboard
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key

# Configuration
BROADCAST_PORT = 54321
COMM_PORT = 54322
BROADCAST_INTERVAL = 2
MAGIC_MESSAGE = b"KVM_SWITCH_DISCOVERY"


class KVMSwitch:
    def __init__(self):
        self.mode = None  # 'server' or 'client'
        self.connected = False
        self.has_control = False
        self.peer_addr = None
        self.sock = None
        self.running = True
        
        # Controllers
        self.mouse_controller = MouseController()
        self.keyboard_controller = KeyboardController()
        
        # Input listeners
        self.mouse_listener = None
        self.keyboard_listener = None
        
        # Screen dimensions
        self.screen_width = 1920
        self.screen_height = 1080
        self.peer_screen_width = 1920
        self.peer_screen_height = 1080
        
        # UI elements
        self.root = None
        self.control_button = None
        self.overlay = None
        
    def get_screen_dimensions(self):
        """Get current screen dimensions"""
        root = tk.Tk()
        root.withdraw()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        return width, height
    
    def show_role_selection(self):
        """Show role selection dialog"""
        root = tk.Tk()
        root.title("KVM Switch - Role Selection")
        root.geometry("350x250")
        root.resizable(False, False)
        
        # Center window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (350 // 2)
        y = (root.winfo_screenheight() // 2) - (250 // 2)
        root.geometry(f"+{x}+{y}")
        
        tk.Label(root, text="KVM Switch Tool", font=("Arial", 16, "bold")).pack(pady=20)
        tk.Label(root, text="Select your role:", font=("Arial", 11)).pack(pady=10)
        
        role_var = tk.StringVar(value="server")
        
        tk.Radiobutton(root, text="Server (Controller)", variable=role_var, 
                      value="server", font=("Arial", 10)).pack(pady=5)
        tk.Radiobutton(root, text="Client (Controlled)", variable=role_var, 
                      value="client", font=("Arial", 10)).pack(pady=5)
        
        def on_ok():
            self.mode = role_var.get()
            root.destroy()
        
        tk.Button(root, text="OK", command=on_ok, width=15, 
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(pady=20)
        
        root.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
        root.mainloop()
    
    def start_discovery(self):
        """Start network discovery"""
        if self.mode == "server":
            threading.Thread(target=self.broadcast_presence, daemon=True).start()
        threading.Thread(target=self.listen_for_peers, daemon=True).start()
    
    def broadcast_presence(self):
        """Broadcast presence on network (server only)"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        while self.running and not self.connected:
            try:
                sock.sendto(MAGIC_MESSAGE, ('<broadcast>', BROADCAST_PORT))
                time.sleep(BROADCAST_INTERVAL)
            except:
                pass
        
        sock.close()
    
    def listen_for_peers(self):
        """Listen for peer discovery messages"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', BROADCAST_PORT))
        sock.settimeout(1.0)
        
        while self.running and not self.connected:
            try:
                data, addr = sock.recvfrom(1024)
                if data == MAGIC_MESSAGE and self.mode == "client":
                    # Client found server
                    if self.request_connection_approval(addr[0]):
                        self.peer_addr = addr[0]
                        self.establish_connection()
                        break
            except socket.timeout:
                continue
            except:
                pass
        
        sock.close()
    
    def request_connection_approval(self, server_ip):
        """Show connection approval dialog (client only)"""
        root = tk.Tk()
        root.withdraw()
        result = messagebox.askyesno(
            "Connection Request",
            f"Server at {server_ip} wants to connect.\nAllow connection?",
            parent=root
        )
        root.destroy()
        return result
    
    def establish_connection(self):
        """Establish TCP connection with peer"""
        try:
            if self.mode == "server":
                # Server listens
                server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_sock.bind(('', COMM_PORT))
                server_sock.listen(1)
                server_sock.settimeout(10.0)
                
                self.sock, addr = server_sock.accept()
                self.peer_addr = addr[0]
                server_sock.close()
            else:
                # Client connects
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.peer_addr, COMM_PORT))
            
            self.sock.settimeout(1.0)
            self.connected = True
            
            # Exchange screen dimensions
            self.exchange_screen_info()
            
            # Start communication thread
            threading.Thread(target=self.handle_communication, daemon=True).start()
            
        except Exception as e:
            self.connected = False
            self.reconnect()
    
    def exchange_screen_info(self):
        """Exchange screen dimensions with peer"""
        try:
            # Send our dimensions
            dims = {"width": self.screen_width, "height": self.screen_height}
            self.sock.sendall(json.dumps(dims).encode() + b'\n')
            
            # Receive peer dimensions
            data = b''
            while b'\n' not in data:
                chunk = self.sock.recv(1024)
                if not chunk:
                    break
                data += chunk
            
            peer_dims = json.loads(data.decode().strip())
            self.peer_screen_width = peer_dims['width']
            self.peer_screen_height = peer_dims['height']
        except:
            pass
    
    def handle_communication(self):
        """Handle incoming messages from peer"""
        buffer = b''
        while self.running and self.connected:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    raise ConnectionError("Connection lost")
                
                buffer += chunk
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)
                    self.process_message(line)
                    
            except socket.timeout:
                continue
            except:
                self.connected = False
                self.reconnect()
                break
    
    def process_message(self, data):
        """Process incoming control message"""
        try:
            msg = json.loads(data.decode())
            
            if msg['type'] == 'control_request':
                # Peer wants control - CLIENT receives control
                if self.mode == "client":
                    self.has_control = True  # Client now has control
                else:
                    self.has_control = False
                if self.mode == "server":
                    self.show_overlay()
                self.update_ui()
                
            elif msg['type'] == 'control_release':
                # Peer released control - SERVER gets control back
                if self.mode == "server":
                    self.has_control = True
                    # Force hide overlay immediately
                    if self.overlay:
                        try:
                            self.overlay.withdraw()
                            self.overlay.destroy()
                        except:
                            pass
                        self.overlay = None
                    self.root.attributes('-topmost', True)
                    self.root.update()
                else:
                    self.has_control = False
                self.update_ui()
                
            elif msg['type'] == 'mouse_move':
                # Receive remote mouse movement - only apply if we DON'T have control
                if self.mode == "client" and self.has_control:
                    # Client has control, so apply server's movements
                    x = int(msg['x'] * self.screen_width)
                    y = int(msg['y'] * self.screen_height)
                    self.mouse_controller.position = (x, y)
                
            elif msg['type'] == 'mouse_click':
                if self.mode == "client" and self.has_control:
                    button = Button.left if msg['button'] == 'left' else Button.right
                    if msg['pressed']:
                        self.mouse_controller.press(button)
                    else:
                        self.mouse_controller.release(button)
                    
            elif msg['type'] == 'mouse_scroll':
                if self.mode == "client" and self.has_control:
                    self.mouse_controller.scroll(msg['dx'], msg['dy'])
                
            elif msg['type'] == 'key':
                if self.mode == "client" and self.has_control:
                    key = msg['key']
                    if msg['pressed']:
                        try:
                            if len(key) == 1:
                                self.keyboard_controller.press(key)
                            else:
                                self.keyboard_controller.press(getattr(Key, key, key))
                        except:
                            pass
                    else:
                        try:
                            if len(key) == 1:
                                self.keyboard_controller.release(key)
                            else:
                                self.keyboard_controller.release(getattr(Key, key, key))
                        except:
                            pass
        except:
            pass
    
    def send_message(self, msg):
        """Send message to peer"""
        try:
            if self.sock and self.connected:
                self.sock.sendall(json.dumps(msg).encode() + b'\n')
        except:
            self.connected = False
            self.reconnect()
    
    def on_mouse_move(self, x, y):
        """Handle mouse movement"""
        if not self.connected:
            return True
            
        if self.mode == "server":
            if not self.has_control:
                # Server with gray overlay - control client
                norm_x = x / self.screen_width
                norm_y = y / self.screen_height
                self.send_message({'type': 'mouse_move', 'x': norm_x, 'y': norm_y})
                return True  # Allow cursor to move on overlay
            else:
                # Server has control - work normally
                return True
        else:  # Client
            if self.has_control:
                # Client has control - allow normal movement
                return True
            else:
                # Client doesn't have control - FREEZE
                return False
    
    def on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click"""
        if not self.connected:
            return True
            
        if self.mode == "server":
            if not self.has_control:
                # Server controlling client
                btn = 'left' if button == Button.left else 'right'
                self.send_message({'type': 'mouse_click', 'button': btn, 'pressed': pressed})
                return True
            else:
                return True
        else:  # Client
            if self.has_control:
                return True
            else:
                return False
    
    def on_mouse_scroll(self, x, y, dx, dy):
        """Handle mouse scroll"""
        if not self.connected:
            return True
            
        if self.mode == "server":
            if not self.has_control:
                # Server controlling client
                self.send_message({'type': 'mouse_scroll', 'dx': dx, 'dy': dy})
                return True
            else:
                return True
        else:  # Client
            if self.has_control:
                return True
            else:
                return False
    
    def on_key_press(self, key):
        """Handle key press"""
        if not self.connected:
            return True
            
        if self.mode == "server":
            if not self.has_control:
                # Server controlling client
                try:
                    k = key.char if hasattr(key, 'char') else key.name
                    self.send_message({'type': 'key', 'key': k, 'pressed': True})
                except:
                    pass
                return True
            else:
                return True
        else:  # Client
            if self.has_control:
                return True
            else:
                return False
    
    def on_key_release(self, key):
        """Handle key release"""
        if not self.connected:
            return True
            
        if self.mode == "server":
            if not self.has_control:
                # Server controlling client
                try:
                    k = key.char if hasattr(key, 'char') else key.name
                    self.send_message({'type': 'key', 'key': k, 'pressed': False})
                except:
                    pass
                return True
            else:
                return True
        else:  # Client
            if self.has_control:
                return True
            else:
                return False
    
    def start_input_capture(self):
        """Start capturing input"""
        # Never suppress - handle blocking in the callbacks
        self.mouse_listener = mouse.Listener(
            on_move=self.on_mouse_move,
            on_click=self.on_mouse_click,
            on_scroll=self.on_mouse_scroll,
            suppress=False  # Don't suppress, we handle it in callbacks
        )
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release,
            suppress=False  # Don't suppress, we handle it in callbacks
        )
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
    
    def toggle_control(self):
        """Toggle control between server and client"""
        if not self.connected:
            return
        
        if self.mode == "server":
            if self.has_control:
                # Server giving control away
                self.has_control = False
                self.send_message({'type': 'control_request'})
                self.show_overlay()
                self.update_ui()
        else:  # Client
            if self.has_control:
                # Client giving control back to server
                self.has_control = False
                self.send_message({'type': 'control_release'})
                self.update_ui()
    
    def show_overlay(self):
        """Show semi-transparent overlay (server only)"""
        if self.overlay:
            return
        
        self.overlay = tk.Toplevel(self.root)
        
        # Get screen dimensions for fullscreen
        screen_width = self.overlay.winfo_screenwidth()
        screen_height = self.overlay.winfo_screenheight()
        
        # Make it truly fullscreen
        self.overlay.geometry(f"{screen_width}x{screen_height}+0+0")
        self.overlay.overrideredirect(True)
        
        # Try to set transparency at window level
        try:
            self.overlay.wait_visibility(self.overlay)
            self.overlay.wm_attributes('-alpha', 0.6)
        except:
            pass
        
        # Create canvas with semi-transparent gray
        canvas = tk.Canvas(self.overlay, width=screen_width, height=screen_height, 
                          bg='gray', highlightthickness=0)
        canvas.pack(fill='both', expand=True)
        
        # Add text to show it's active
        canvas.create_text(screen_width//2, screen_height//2,
                          text="Server Overlay Active\nClient has control",
                          font=("Arial", 24),
                          fill="white")
        
        self.overlay.attributes('-topmost', True)
        self.overlay.update_idletasks()
        
        # Lower below button
        self.overlay.lower()
        
        # Keep control button on top
        self.root.attributes('-topmost', True)
        self.root.lift()
        
        self.overlay.update()
    
    def hide_overlay(self):
        """Hide overlay"""
        if self.overlay:
            try:
                self.overlay.withdraw()  # Hide first
                self.overlay.destroy()   # Then destroy
                self.overlay.update()    # Force update
            except:
                pass
            self.overlay = None
        
        # Reset button topmost and force refresh
        try:
            self.root.attributes('-topmost', True)
            self.root.update()
        except:
            pass
    
    def update_ui(self):
        """Update UI based on control state"""
        if not self.control_button:
            return
        
        if not self.connected:
            color = "gray"
            text = "Disconnected"
            state = "disabled"
        elif self.has_control:
            color = "green"
            text = "You Have Control"
            state = "normal"
        else:
            color = "red"
            text = "No Control"
            # CLIENT button always clickable to return control
            # SERVER button disabled when no control
            state = "normal" if self.mode == "client" else "disabled"
        
        self.control_button.config(bg=color, text=text, state=state)
    
    def create_ui(self):
        """Create main UI"""
        self.root = tk.Tk()
        self.root.title("KVM Switch")
        self.root.geometry("200x80")
        self.root.attributes('-topmost', True)
        
        # Position at top-right
        self.root.update_idletasks()
        x = self.root.winfo_screenwidth() - 220
        y = 20
        self.root.geometry(f"+{x}+{y}")
        
        self.control_button = tk.Button(
            self.root,
            text="Connecting...",
            command=self.toggle_control,
            font=("Arial", 10, "bold"),
            fg="white",
            bg="gray",
            width=20,
            height=3
        )
        self.control_button.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.root.protocol("WM_DELETE_WINDOW", self.cleanup)
        
        # Wait for connection before updating UI
        def wait_for_connection():
            while not self.connected and self.running:
                time.sleep(0.1)
            
            if self.mode == "server":
                self.has_control = True
            
            self.update_ui()
        
        threading.Thread(target=wait_for_connection, daemon=True).start()
    
    def reconnect(self):
        """Attempt to reconnect"""
        if not self.running:
            return
        
        self.connected = False
        self.has_control = False
        self.hide_overlay()
        self.update_ui()
        
        time.sleep(2)
        self.start_discovery()
    
    def cleanup(self):
        """Cleanup resources"""
        self.running = False
        self.connected = False
        
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        if self.overlay:
            self.overlay.destroy()
        if self.root:
            self.root.destroy()
        
        sys.exit(0)
    
    def run(self):
        """Main run method"""
        # Get screen dimensions
        self.screen_width, self.screen_height = self.get_screen_dimensions()
        
        # Show role selection
        self.show_role_selection()
        
        if not self.mode:
            return
        
        # Start input capture
        self.start_input_capture()
        
        # Start discovery
        self.start_discovery()
        
        # If server, also start listening for connections
        if self.mode == "server":
            threading.Thread(target=self.wait_for_client, daemon=True).start()
        
        # Create and run UI
        self.create_ui()
        self.root.mainloop()
    
    def wait_for_client(self):
        """Wait for client connection (server only)"""
        while self.running and not self.connected:
            try:
                self.establish_connection()
            except:
                time.sleep(1)


def main():
    """Main entry point"""
    print("✅ KVM Switch Tool - Starting...")
    app = KVMSwitch()
    try:
        app.run()
    except KeyboardInterrupt:
        app.cleanup()
    except Exception as e:
        print(f"Error: {e}")
        app.cleanup()


if __name__ == "__main__":
    main()
