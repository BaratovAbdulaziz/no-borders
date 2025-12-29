"""
Control panel UI for the KVM Switch application
"""

import tkinter as tk
from tkinter import messagebox
import sys
from typing import Optional, Callable
from ..utils.config import (CONTROL_PANEL_WIDTH, CONTROL_PANEL_HEIGHT, 
                           UI_COLORS, FONTS)

class ControlPanel:
    """
    Main control panel UI for managing KVM switch state
    
    This class provides the primary user interface for controlling
    the KVM switch, including connection status and control toggle.
    """
    
    def __init__(self, toggle_callback: Optional[Callable] = None, 
                 cleanup_callback: Optional[Callable] = None):
        """
        Initialize the control panel
        
        Args:
            toggle_callback: Callback function for control toggle button
            cleanup_callback: Callback function for cleanup on close
        """
        self.toggle_callback = toggle_callback
        self.cleanup_callback = cleanup_callback
        self.root: Optional[tk.Tk] = None
        self.control_button: Optional[tk.Button] = None
        
    def create(self) -> None:
        """Create the control panel UI"""
        self.root = tk.Tk()
        self.root.title("KVM Switch")
        self.root.geometry(f"{CONTROL_PANEL_WIDTH}x{CONTROL_PANEL_HEIGHT}")
        self.root.attributes('-topmost', True)
        
        # Position at top-right
        self.root.update_idletasks()
        x = self.root.winfo_screenwidth() - CONTROL_PANEL_WIDTH - 20
        y = 20
        self.root.geometry(f"+{x}+{y}")
        
        self.control_button = tk.Button(
            self.root,
            text="Connecting...",
            command=self._on_toggle,
            font=FONTS['control_button'],
            fg="white",
            bg=UI_COLORS['disconnected'],
            width=20,
            height=3
        )
        self.control_button.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
    def _on_toggle(self) -> None:
        """Handle toggle button click"""
        if self.toggle_callback:
            self.toggle_callback()
            
    def _on_close(self) -> None:
        """Handle window close event"""
        if self.cleanup_callback:
            self.cleanup_callback()
        else:
            sys.exit(0)
    
    def update_state(self, connected: bool, has_control: bool, mode: str) -> None:
        """
        Update UI based on current state
        
        Args:
            connected: Whether the application is connected to peer
            has_control: Whether the local instance has control
            mode: Operating mode ('server' or 'client')
        """
        if not self.control_button:
            return
        
        if not connected:
            color = UI_COLORS['disconnected']
            text = "Disconnected"
            state = "disabled"
        elif has_control:
            color = UI_COLORS['connected']
            text = "You Have Control"
            state = "normal"
        else:
            color = UI_COLORS['no_control']
            text = "No Control"
            # CLIENT button always clickable to return control
            # SERVER button disabled when no control
            state = "normal" if mode == "client" else "disabled"
        
        self.control_button.config(bg=color, text=text, state=state)
        
    def bring_to_front(self) -> None:
        """Bring the control panel to the front"""
        if self.root:
            self.root.attributes('-topmost', True)
            self.root.lift()
            self.root.update()
    
    def run(self) -> None:
        """Start the UI main loop"""
        if self.root:
            self.root.mainloop()
    
    def destroy(self) -> None:
        """Destroy the control panel"""
        if self.root:
            self.root.destroy()

def show_role_selection_dialog() -> Optional[str]:
    """
    Show role selection dialog
    
    Returns:
        Optional[str]: Selected role ('server' or 'client') or None if cancelled
    """
    root = tk.Tk()
    root.title("KVM Switch - Role Selection")
    root.geometry("350x250")
    root.resizable(False, False)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (350 // 2)
    y = (root.winfo_screenheight() // 2) - (250 // 2)
    root.geometry(f"+{x}+{y}")
    
    tk.Label(root, text="KVM Switch Tool", 
             font=("Arial", 16, "bold")).pack(pady=20)
    tk.Label(root, text="Select your role:", 
             font=("Arial", 11)).pack(pady=10)
    
    role_var = tk.StringVar(value="server")
    
    tk.Radiobutton(root, text="Server (Controller)", 
                   variable=role_var, value="server", 
                   font=("Arial", 10)).pack(pady=5)
    tk.Radiobutton(root, text="Client (Controlled)", 
                   variable=role_var, value="client", 
                   font=("Arial", 10)).pack(pady=5)
    
    result = [None]
    
    def on_ok():
        result[0] = role_var.get()
        root.destroy()
    
    tk.Button(root, text="OK", command=on_ok, width=15, 
              bg="#4CAF50", fg="white", 
              font=("Arial", 10, "bold")).pack(pady=20)
    
    root.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
    root.mainloop()
    
    return result[0]

def show_connection_approval_dialog(server_ip: str) -> bool:
    """
    Show connection approval dialog (client only)
    
    Args:
        server_ip: IP address of the server requesting connection
        
    Returns:
        bool: True if connection is approved, False otherwise
    """
    root = tk.Tk()
    root.withdraw()
    result = messagebox.askyesno(
        "Connection Request",
        f"Server at {server_ip} wants to connect.\nAllow connection?",
        parent=root
    )
    root.destroy()
    return result