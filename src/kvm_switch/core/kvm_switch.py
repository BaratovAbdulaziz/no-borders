"""
Main KVM Switch application class
"""

import tkinter as tk
import threading
import time
import sys
from typing import Optional

from ..utils.config import DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT
from ..ui.splash import SplashScreen
from ..ui.control_panel import ControlPanel, show_role_selection_dialog
from ..ui.overlay import ServerOverlay
from ..core.network import NetworkManager
from ..handlers.input_handler import InputHandler
from ..handlers.message_handler import MessageHandler

class KVMSwitch:
    """
    Main KVM Switch application class
    
    This class coordinates all components of the KVM switch including
    networking, input handling, UI management, and message processing.
    """
    
    def __init__(self):
        """Initialize the KVM Switch application"""
        self.mode: Optional[str] = None  # 'server' or 'client'
        self.connected = False
        self.has_control = False
        self.running = True
        
        # Screen dimensions
        self.screen_width = DEFAULT_SCREEN_WIDTH
        self.screen_height = DEFAULT_SCREEN_HEIGHT
        self.peer_screen_width = DEFAULT_SCREEN_WIDTH
        self.peer_screen_height = DEFAULT_SCREEN_HEIGHT
        
        # Component instances
        self.network_manager: Optional[NetworkManager] = None
        self.input_handler: Optional[InputHandler] = None
        self.message_handler: Optional[MessageHandler] = None
        self.control_panel: Optional[ControlPanel] = None
        self.overlay: Optional[ServerOverlay] = None
        
    def get_screen_dimensions(self) -> tuple[int, int]:
        """
        Get current screen dimensions
        
        Returns:
            tuple[int, int]: Screen width and height
        """
        root = tk.Tk()
        root.withdraw()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        return width, height

    def show_splash_screen(self) -> None:
        """Show animated No-Borders brand splash screen"""
        splash = SplashScreen()
        splash.show()

    def show_role_selection(self) -> None:
        """Show role selection dialog"""
        self.mode = show_role_selection_dialog()
    
    def initialize_components(self) -> None:
        """Initialize all application components"""
        if not self.mode:
            return
            
        # Initialize network manager
        self.network_manager = NetworkManager(
            self.mode, 
            self.on_message_received
        )
        
        # Initialize input handler
        self.input_handler = InputHandler(
            self.mode, 
            self.send_message
        )
        
        # Initialize message handler
        self.message_handler = MessageHandler(
            self.mode,
            self.input_handler,
            self.on_control_state_changed,
            self.show_overlay,
            self.hide_overlay
        )
        
        # Initialize control panel
        self.control_panel = ControlPanel(
            self.toggle_control,
            self.cleanup
        )
        
        # Set up screen dimensions
        self.input_handler.set_screen_dimensions(
            self.screen_width, self.screen_height,
            self.peer_screen_width, self.peer_screen_height
        )
    
    def on_message_received(self, data: bytes) -> None:
        """
        Handle received messages from network
        
        Args:
            data: Raw message data
        """
        if self.message_handler:
            self.message_handler.process_message(data)
    
    def send_message(self, msg: dict) -> None:
        """
        Send message to peer
        
        Args:
            msg: Message dictionary to send
        """
        if self.network_manager:
            self.network_manager.send_message(msg)
    
    def on_control_state_changed(self, has_control: bool) -> None:
        """
        Handle control state changes
        
        Args:
            has_control: Whether local instance has control
        """
        self.has_control = has_control
        self.update_ui()
    
    def show_overlay(self) -> None:
        """Show server overlay"""
        if self.mode == "server" and self.control_panel:
            if not self.overlay:
                self.overlay = ServerOverlay(self.control_panel.root)
            self.overlay.show()
    
    def hide_overlay(self) -> None:
        """Hide server overlay"""
        if self.overlay:
            self.overlay.hide()
            self.overlay = None
        
        # Bring control panel to front
        if self.control_panel:
            self.control_panel.bring_to_front()
    
    def update_ui(self) -> None:
        """Update UI based on current state"""
        if self.control_panel:
            self.control_panel.update_state(
                self.connected, self.has_control, self.mode
            )
    
    def toggle_control(self) -> None:
        """Toggle control between server and client"""
        if not self.connected or not self.network_manager:
            return
        
        if self.mode == "server":
            if self.has_control:
                # Server giving control away
                self.has_control = False
                self.network_manager.send_message({'type': 'control_request'})
                self.show_overlay()
                self.update_ui()
        else:  # Client
            if self.has_control:
                # Client giving control back to server
                self.has_control = False
                self.network_manager.send_message({'type': 'control_release'})
                self.update_ui()
    
    def start_discovery(self) -> None:
        """Start network discovery"""
        if self.network_manager:
            self.network_manager.start_discovery()
    
    def wait_for_connection(self) -> None:
        """Wait for connection to be established"""
        def connection_loop():
            while not self.connected and self.running:
                if self.network_manager and self.network_manager.connected:
                    self.connected = True
                    
                    # Exchange screen info
                    peer_width, peer_height = self.network_manager.exchange_screen_info(
                        self.screen_width, self.screen_height
                    )
                    self.peer_screen_width = peer_width
                    self.peer_screen_height = peer_height
                    
                    # Update input handler with new dimensions
                    if self.input_handler:
                        self.input_handler.set_screen_dimensions(
                            self.screen_width, self.screen_height,
                            peer_width, peer_height
                        )
                        self.input_handler.set_state(True, self.has_control)
                    
                    # Set initial control state
                    if self.mode == "server":
                        self.has_control = True
                    
                    self.update_ui()
                    break
                
                time.sleep(0.1)
            
            # Monitor connection
            while self.connected and self.running:
                if self.network_manager and not self.network_manager.connected:
                    self.reconnect()
                    break
                time.sleep(1)
        
        threading.Thread(target=connection_loop, daemon=True).start()
        
        # If server, also start listening for connections
        if self.mode == "server" and self.network_manager:
            threading.Thread(target=self.network_manager.wait_for_client, daemon=True).start()
    
    def reconnect(self) -> None:
        """Attempt to reconnect"""
        if not self.running:
            return
        
        self.connected = False
        self.has_control = False
        self.hide_overlay()
        self.update_ui()
        
        if self.network_manager:
            self.network_manager.reconnect()
        
        # Restart connection monitoring
        self.wait_for_connection()
    
    def cleanup(self) -> None:
        """Cleanup resources and exit"""
        self.running = False
        self.connected = False
        
        if self.input_handler:
            self.input_handler.stop_input_capture()
            
        if self.network_manager:
            self.network_manager.disconnect()
            
        if self.overlay:
            self.overlay.hide()
            
        if self.control_panel:
            self.control_panel.destroy()
        
        sys.exit(0)
    
    def run(self) -> None:
        """Main run method"""
        # Get screen dimensions
        self.screen_width, self.screen_height = self.get_screen_dimensions()

        # Show splash screen animation
        self.show_splash_screen()

        # Show role selection
        self.show_role_selection()
        
        if not self.mode:
            return
        
        # Initialize all components
        self.initialize_components()
        
        # Start input capture
        if self.input_handler:
            self.input_handler.start_input_capture()
        
        # Start discovery
        self.start_discovery()
        
        # Wait for connection
        self.wait_for_connection()
        
        # Create and run UI
        if self.control_panel:
            self.control_panel.create()
            self.control_panel.run()

def main() -> None:
    """Main entry point"""
    print("No-Borders KVM Switch - Starting...")
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