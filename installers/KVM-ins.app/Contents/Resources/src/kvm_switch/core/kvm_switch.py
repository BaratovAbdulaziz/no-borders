"""
Main KVM Switch class for No-Borders seamless multi-computer control
"""
import sys
import time
import threading
import socket
import os
from typing import Optional, Set, Dict, Any, List

from ..utils.config import (
    APP_VERSION, LICENSE, DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT,
    CONNECTION_TIMEOUT, SERVER_TIMEOUT, MESSAGE_TIMEOUT, RECONNECT_DELAY,
    INDICATOR_UPDATE_INTERVAL, INDICATOR_WIDTH, INDICATOR_HEIGHT
)
from .network import NetworkManager
from ..ui.splash import SplashScreen
from ..ui.control_panel_fixed import ControlPanel
from ..ui.overlay import OverlayManager
from ..handlers.input_handler import InputHandler
from ..handlers.message_handler import MessageHandler


class KVMSwitch:
    """
    Main KVM Switch class that coordinates all components
    """
    
    def __init__(self) -> None:
        """Initialize the KVM Switch"""
        # Core state
        self.mode: Optional[str] = None  # 'server' or 'client'
        self.control_method: str = "button"  # 'button' or 'hotkey'
        self.connected: bool = False
        self.has_control: bool = False
        self.peer_addr: Optional[str] = None
        self.running: bool = True
        
        # Network socket
        self.sock: Optional[socket.socket] = None
        
        # Screen dimensions
        self.screen_width: int = DEFAULT_SCREEN_WIDTH
        self.screen_height: int = DEFAULT_SCREEN_HEIGHT
        
        # Network manager
        self.network_manager = NetworkManager(self)
        
        # UI components
        self.splash: Optional[SplashScreen] = None
        self.control_panel: Optional[ControlPanel] = None
        self.overlay_manager: Optional[OverlayManager] = None
        
        # Input handling
        self.input_handler: Optional[InputHandler] = None
        
        # Message handling
        self.message_handler: Optional[MessageHandler] = None
        
        # Hotkey support
        self.hotkey_combo: List[str] = []
        self.current_keys: Set[str] = set()
        
        # UI state
        self.root = None
        self.indicator_label = None
        self.toggle_btn = None
        
        # Connection state
        self._connecting = False
    
    def initialize_screen_dimensions(self) -> None:
        """Get actual screen dimensions"""
        try:
            import tkinter as tk
            temp = tk.Tk()
            self.screen_width = temp.winfo_screenwidth()
            self.screen_height = temp.winfo_screenheight()
            temp.destroy()
        except Exception as e:
            print(f"Warning: Could not get screen dimensions: {e}")
            print(f"Using defaults: {self.screen_width}x{self.screen_height}")
    
    def show_splash(self) -> None:
        """Show animated splash screen"""
        self.splash = SplashScreen()
        self.splash.show()
    
    def show_setup(self) -> None:
        """Show setup dialog and get configuration"""
        self.control_panel = ControlPanel(self)
        self.control_panel.show()
    
    def start(self) -> None:
        """Start the KVM Switch application"""
        print(f"⚡ No-Borders v{APP_VERSION} - Starting...")
        
        # Initialize screen dimensions
        self.initialize_screen_dimensions()
        print(f"Screen: {self.screen_width}x{self.screen_height}")
        
        # Show splash screen
        self.show_splash()
        
        # Show setup dialog
        self.show_setup()
        
        if not self.mode:
            print("Setup cancelled")
            return
        
        print(f"Starting in {self.mode} mode with {self.control_method} control")
        
        # Initialize handlers
        self.input_handler = InputHandler(self)
        self.message_handler = MessageHandler(self)
        self.overlay_manager = OverlayManager(self)
        
        # Start components
        self.input_handler.start()
        self.network_manager.start()
        
        # Start connection attempt
        if self.mode == "server":
            threading.Thread(target=self._connect, daemon=True).start()
        
        # Create and show indicator
        self._create_indicator()
        
        # Run main loop
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nShutdown requested")
            self.cleanup()
    
    def _connect(self) -> None:
        """Establish connection with peer"""
        # Prevent multiple connection attempts
        if self._connecting:
            return
        
        self._connecting = True
        
        try:
            if self.mode == "server":
                print("Server: Waiting for client connection...")
                self.network_manager.start_server()
            else:  # client
                print(f"Client: Connecting to server at {self.peer_addr}")
                self.network_manager.connect_to_server(self.peer_addr)
            
            self.connected = True
            self.has_control = (self.mode == "server")
            
            print(f"✓ Connection established! Mode: {self.mode}, Has control: {self.has_control}")
            
            # Start message handling
            if self.message_handler:
                threading.Thread(target=self.message_handler.handle_messages, daemon=True).start()
            
        except Exception as e:
            print(f"Connection error: {e}")
            self.connected = False
            if self.running:
                time.sleep(RECONNECT_DELAY)
                self._connecting = False
                threading.Thread(target=self._connect, daemon=True).start()
        finally:
            self._connecting = False
    
    def toggle_control(self) -> None:
        """Toggle control between machines"""
        if not self.connected:
            print("Cannot toggle - not connected")
            return
        
        print(f"Toggling control from mode: {self.mode}")
        
        # Send toggle message
        if self.message_handler:
            self.message_handler.send_message({'type': 'toggle'})
        
        # Update local state
        self.has_control = not self.has_control
        
        # Update overlay
        if self.overlay_manager:
            if not self.has_control:
                self.overlay_manager.show_overlay()
            else:
                self.overlay_manager.hide_overlay()
    
    def _create_indicator(self) -> None:
        """Create status indicator window"""
        import tkinter as tk
        from tkinter import font as tkfont
        
        self.root = tk.Tk()
        self.root.title("No-Borders")
        self.root.geometry(f"{INDICATOR_WIDTH}x{INDICATOR_HEIGHT}")
        self.root.configure(bg="#0f0f0f")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        
        # Position top-right
        x = self.root.winfo_screenwidth() - INDICATOR_WIDTH - 20
        y = 20
        self.root.geometry(f"+{x}+{y}")
        
        # Make draggable
        self.root.bind('<Button-1>', self._start_drag)
        self.root.bind('<B1-Motion>', self._on_drag)
        
        # Create indicator frame
        frame = tk.Frame(self.root, bg="#1a1a1a", highlightbackground="#2a2a2a", highlightthickness=1)
        frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Header with exit button
        header = tk.Frame(frame, bg="#1a1a1a")
        header.pack(fill="x", padx=5, pady=(5, 0))
        
        # Make header draggable
        header.bind('<Button-1>', self._start_drag)
        header.bind('<B1-Motion>', self._on_drag)
        
        # Title
        title_label = tk.Label(header, text="⚡ No-Borders", font=("Arial", 9, "bold"),
                               bg="#1a1a1a", fg="#818cf8")
        title_label.pack(side="left")
        title_label.bind('<Button-1>', self._start_drag)
        title_label.bind('<B1-Motion>', self._on_drag)
        
        # Exit button
        exit_btn = tk.Label(header, text="✕", font=("Arial", 14, "bold"),
                           bg="#1a1a1a", fg="#6b7280", cursor="hand2", padx=5)
        exit_btn.pack(side="right")
        exit_btn.bind('<Button-1>', lambda e: self.cleanup())
        exit_btn.bind('<Enter>', lambda e: exit_btn.config(fg="#ef4444"))
        exit_btn.bind('<Leave>', lambda e: exit_btn.config(fg="#6b7280"))
        
        # Status indicator
        self.indicator_label = tk.Label(frame, text="🟡 CONNECTING", font=("Arial", 11, "bold"),
                                       bg="#1a1a1a", fg="#fbbf24", pady=8)
        self.indicator_label.pack(fill="x")
        self.indicator_label.bind('<Button-1>', self._start_drag)
        self.indicator_label.bind('<B1-Motion>', self._on_drag)
        
        # Add toggle button if button mode
        if self.mode == "server" and self.control_method == "button":
            btn = tk.Button(frame, text="TOGGLE CONTROL", command=self.toggle_control,
                           bg="#818cf8", fg="white", font=("Arial", 10, "bold"),
                           bd=0, state="disabled", pady=8)
            btn.pack(fill="x", padx=5, pady=(0, 5))
            self.toggle_btn = btn
        
        self.root.protocol("WM_DELETE_WINDOW", self.cleanup)
        threading.Thread(target=self._update_indicator, daemon=True).start()
    
    def _start_drag(self, event) -> None:
        """Start dragging the indicator"""
        self._drag_x = event.x
        self._drag_y = event.y
    
    def _on_drag(self, event) -> None:
        """Handle dragging the indicator"""
        try:
            x = self.root.winfo_x() + event.x - self._drag_x
            y = self.root.winfo_y() + event.y - self._drag_y
            self.root.geometry(f"+{x}+{y}")
        except:
            pass
    
    def _update_indicator(self) -> None:
        """Update indicator status"""
        while self.running:
            time.sleep(INDICATOR_UPDATE_INTERVAL)
            try:
                if not self.connected:
                    text, color = "🟡 CONNECTING", "#fbbf24"
                    btn_state = "disabled"
                elif self.has_control:
                    text = "🟢 IN CONTROL"
                    if self.control_method == "hotkey":
                        text += " 🔥"
                    color = "#10b981"
                    btn_state = "normal"
                else:
                    text, color = "🔴 PEER CONTROL", "#ef4444"
                    btn_state = "normal"
                
                if self.indicator_label:
                    self.indicator_label.config(text=text, fg=color)
                
                if hasattr(self, 'toggle_btn') and self.toggle_btn:
                    self.toggle_btn.config(state=btn_state)
            except:
                pass
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        print("Cleaning up...")
        self.running = False
        self.connected = False
        
        # Stop input handler
        if self.input_handler:
            self.input_handler.stop()
        
        # Stop network manager
        if self.network_manager:
            self.network_manager.stop()
        
        # Close overlay
        if self.overlay_manager:
            self.overlay_manager.hide_overlay()
        
        # Close root window
        if self.root:
            try:
                self.root.destroy()
            except:
                pass
        
        sys.exit(0)